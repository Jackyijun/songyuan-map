# -*- coding: utf-8 -*-
"""宋辽夏金元形势图 · 数据构建。

读 content/ 的史料与 geodata/ 的底图，算出每个时间节点的疆域多边形，
写出 build/geo.json（几何）和 build/data.json（条目与说明）。

流程（规范第十三节）：
  1. 读归属点（seeds.txt）、单位（units.py）、时间节点（snaps.txt）
  2. 在投影平面上建等距栅格，把海陆、大湖栅格化
  3. 建通行代价栅格：地形起伏、高原、山脊（带横向摆动）、界河，再乘多尺度平滑噪声
  4. 以全部归属点为源做 16 邻接多源最短路，每个格子归代价距离最近的点
  5. 超出可达代价的为无主地；外缘闭运算、平滑，小空隙并回相邻一方；再加一层平滑位移场
  6. 每个节点按“点 → 二级单位 → 政权”归属给格子分类；各类高斯平滑后，
     在相邻两类平滑值相等处描界（沿格边插值，交汇点取均值），界线网络只描一次、两侧共用，
     拉普拉斯平滑后拼成覆盖图，再用 GEOS coverage_simplify 整体简化；政权 = 所属单位之并
  7. 给相邻单位挑低饱和、互相区分的颜色（衔接唐宋图的政权沿用原色）
  8. 整理底图（海岸、河湖、运河、山脉、荒漠、今国界）与点、线条目
"""
import json, re, sys, math, gzip, zlib, time
import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from skimage import measure
from PIL import Image, ImageDraw
import shapely
from shapely.geometry import shape, box, LineString, Polygon, MultiPolygon, MultiLineString
from shapely.ops import unary_union

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
sys.path.insert(0, str(C.CONTENT))
import units as UM
import items as IM

LON0, LON1, LAT0, LAT1 = C.EXTENT
T0 = time.time()
BB = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
EXT_BOX = box(LON0, LAT0, LON1, LAT1)
DEG = 1000 * math.pi / 180          # 一个纬度合多少投影单位（≈17.45）

# ======================================================================
# 0. 投影（与前端 proj() 完全一致）
# ======================================================================
RAD = math.pi / 180
_P1, _P2, _P0, _L0 = [v * RAD for v in C.PROJ]
NN = (math.sin(_P1) + math.sin(_P2)) / 2
CC = math.cos(_P1) ** 2 + 2 * NN * math.sin(_P1)
RHO0 = math.sqrt(CC - 2 * NN * math.sin(_P0)) / NN

def fwd(lon, lat):
    lon = np.asarray(lon, float); lat = np.asarray(lat, float)
    r = np.sqrt(np.maximum(CC - 2 * NN * np.sin(lat * RAD), 1e-9)) / NN
    th = NN * (lon * RAD - _L0)
    return r * np.sin(th) * C.SCL, -(RHO0 - r * np.cos(th)) * C.SCL

def inv(x, y):
    X = np.asarray(x, float) / C.SCL; Y = RHO0 + np.asarray(y, float) / C.SCL
    r = np.hypot(X, Y); th = np.arctan2(X, Y)
    lon = (_L0 + th / NN) / RAD
    lat = np.arcsin(np.clip((CC - (r * NN) ** 2) / (2 * NN), -1, 1)) / RAD
    return lon, lat

def to_xy(g): return shapely.transform(g, lambda a: np.column_stack(fwd(a[:, 0], a[:, 1])))
def to_ll(g): return shapely.transform(g, lambda a: np.column_stack(inv(a[:, 0], a[:, 1])))

def enc_ring(coords):
    """坐标 ×100 取整后差分编码；前端 decode() 还原。"""
    out = []; px = py = 0
    for i, (x, y) in enumerate(coords):
        X, Y = int(round(x * 100)), int(round(y * 100))
        if i == 0: out += [X, Y]
        else:
            if X == px and Y == py: continue
            out += [X - px, Y - py]
        px, py = X, Y
    return out

def polys_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    if g.geom_type in ("MultiPolygon", "GeometryCollection"): return [p for x in g.geoms for p in polys_of(x)]
    return []
def lines_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "LineString": return [g]
    if g.geom_type in ("MultiLineString", "GeometryCollection"): return [p for x in g.geoms for p in lines_of(x)]
    return []
def ne(name): return json.load(open(C.NE_DIR / f"{name}.geojson", encoding="utf8"))
def crc(s): return zlib.crc32(s.encode("utf8"))

# ======================================================================
# 1. 归属点（州府、城邑、区域辅助点）
# ======================================================================
SEEDS = []
for line in open(C.CONTENT / "seeds.txt", encoding="utf8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    t = line.split()
    sid, lo, la, mod = t[0], float(t[1]), float(t[2]), t[3]
    typ, names, reach = "z", None, 1.0
    for x in t[4:]:
        if x in ("c", "r", "z"): typ = x
        elif x.startswith("N="):
            names = []
            for part in x[2:].split(","):
                y, n = part.split(":", 1); names.append([int(y), n])
        elif x.startswith("R="): reach = float(x[2:])
        else: raise SystemExit(f"seeds.txt 无法识别的字段：{line}")
    assert LON0 < lo < LON1 and LAT0 < la < LAT1, ("归属点在全图范围外", sid)
    SEEDS.append(dict(id=sid, n=sid.split("·")[0], lon=lo, lat=la, mod=mod, t=typ, names=names, R=reach))
SID = {s["id"]: i for i, s in enumerate(SEEDS)}
assert len(SID) == len(SEEDS), "seeds.txt 中有重复的 ID：" + str([s["id"] for s in SEEDS if [x["id"] for x in SEEDS].count(s["id"]) > 1][:5])
print("seeds", len(SEEDS))

# ======================================================================
# 2. 单位与时间节点（解析 snaps.txt）
# ======================================================================
UNITS = UM.U
UK = {u["k"]: i for i, u in enumerate(UNITS)}
assert len(UK) == len(UNITS), "units.py 中有重复的键"

SNAPS = []
state = dict(own={}, lab={}, pol={}, seat={}, hatch=set())
cur = None; history = {}; start = None
def snapshot(): return dict(own=dict(state["own"]), lab=dict(state["lab"]), pol=dict(state["pol"]), seat=dict(state["seat"]), hatch=set(state["hatch"]))

for ln, raw in enumerate(open(C.CONTENT / "snaps.txt", encoding="utf8"), 1):
    line = raw.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"): continue
    if line.startswith("@"):
        if cur: history[cur["y"]] = snapshot(); SNAPS.append(dict(cur, st=history[cur["y"]]))
        parts = [p.strip() for p in line[1:].split("|")]
        assert len(parts) == 4, ("节点行应有 4 段：年份 | 年号 | 标题 | 概述", ln)
        cur = dict(y=int(parts[0]), era=parts[1], t=parts[2], d=parts[3])
        assert not SNAPS or cur["y"] > SNAPS[-1]["y"], ("节点年份须递增", cur["y"])
        start = dict(own=dict(state["own"]))
        continue
    head, _, body = line.partition(":")
    head = head.strip(); toks = body.split()
    if head in ("割据", "藩属"):            # 整行替换：本节点起这些单位加斜线
        state["hatch"] = set(toks)
        for k in toks: assert k in UK, ("斜线行里的单位不存在", k, ln)
        continue
    if head in ("+藩属", "-藩属"):          # 增减
        for k in toks:
            assert k in UK, ("斜线行里的单位不存在", k, ln)
            (state["hatch"].add if head[0] == "+" else state["hatch"].discard)(k)
        continue
    if head == "·":
        for tk in toks:
            assert tk in SID, ("未知归属点", tk, cur["y"], ln); state["own"][tk] = None
        continue
    m = re.match(r"^([^\[\]{}>]+)(?:\[([^\]]*)\])?(?:\{([^}]*)\})?(?:>(.+))?$", head)
    assert m, ("无法解析的行", ln, head)
    uk, lab, seat, pol = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
    assert uk in UK, ("units.py 里没有这个单位", uk, cur["y"], ln)
    if lab is not None:
        if lab == "": state["lab"].pop(uk, None)
        else: state["lab"][uk] = lab
    if seat is not None:
        if seat == "": state["seat"].pop(uk, None)
        else:
            assert seat in SID, ("治所不在 seeds.txt", seat, ln); state["seat"][uk] = seat
    if pol is not None:
        assert pol.strip() in UK, ("所属政权不存在", pol, ln); state["pol"][uk] = pol.strip()
    for tk in toks:
        if tk.startswith("@"):
            ref = tk[1:]
            if "@" in ref:   # @单位@年份：取该年节点结束时该单位的点
                rk, ry = ref.split("@"); src = history[int(ry)]["own"]
            else:
                rk = ref; src = start["own"]
            assert rk in UK, ("引用的单位不存在", rk, ln)
            lst = [s for s, u in src.items() if u == rk]
            if not lst: print("  WARN 空引用", tk, "in", cur["y"])
            for s in lst: state["own"][s] = uk
        else:
            assert tk in SID, ("未知归属点", tk, cur["y"], uk, ln); state["own"][tk] = uk
history[cur["y"]] = snapshot()
SNAPS.append(dict(cur, st=history[cur["y"]]))
print("snaps", len(SNAPS), [s["y"] for s in SNAPS])
for sn in SNAPS:
    missing = [s["id"] for s in SEEDS if s["id"] not in sn["st"]["own"]]
    if missing: print("  未分配 at", sn["y"], missing[:30], "…" if len(missing) > 30 else "")

def pol_of(st, uk): return st["pol"].get(uk, UNITS[UK[uk]]["pol"])

# ======================================================================
# 3. 投影平面栅格、海陆
# ======================================================================
_lo = np.r_[np.linspace(LON0, LON1, 400), np.full(200, LON1), np.linspace(LON1, LON0, 400), np.full(200, LON0)]
_la = np.r_[np.full(400, LAT1), np.linspace(LAT1, LAT0, 200), np.full(400, LAT0), np.linspace(LAT0, LAT1, 200)]
_bx, _by = fwd(_lo, _la)
CELL = C.CELL
GX0 = math.floor(_bx.min() / CELL) * CELL - 2 * CELL; GY0 = math.floor(_by.min() / CELL) * CELL - 2 * CELL
NX = int(math.ceil((_bx.max() - GX0) / CELL)) + 2; NY = int(math.ceil((_by.max() - GY0) / CELL)) + 2
XC = GX0 + (np.arange(NX) + 0.5) * CELL; YC = GY0 + (np.arange(NY) + 0.5) * CELL
LONC, LATC = inv(XC[None, :], YC[:, None])
LONC = LONC.astype(np.float32); LATC = LATC.astype(np.float32)
INEXT = (LONC >= LON0) & (LONC <= LON1) & (LATC >= LAT0) & (LATC <= LAT1)
print("grid", NX, "x", NY, "=", NX * NY, "cells; in extent", int(INEXT.sum()))

def xy_to_rc(x, y): return (np.asarray(y) - GY0) / CELL - 0.5, (np.asarray(x) - GX0) / CELL - 0.5
def rc_to_ll(r, c): return inv(GX0 + (np.asarray(c) + 0.5) * CELL, GY0 + (np.asarray(r) + 0.5) * CELL)

def rasterize(geoms_ll):
    """多边形（经纬度）→ 格子掩膜。每块多边形在自己的外接框里用 PIL 扫描线填充（外环填 1、内环填 0）再并入。"""
    m = np.zeros((NY, NX), bool)
    for g in geoms_ll:
        for p in polys_of(to_xy(g)):
            e = np.asarray(p.exterior.coords); r, c = xy_to_rc(e[:, 0], e[:, 1])
            r0, r1 = max(0, int(r.min()) - 1), min(NY, int(r.max()) + 2); c0, c1 = max(0, int(c.min()) - 1), min(NX, int(c.max()) + 2)
            if r1 <= r0 or c1 <= c0: continue
            im = Image.new("1", (c1 - c0, r1 - r0), 0); dr = ImageDraw.Draw(im)
            dr.polygon(list(zip(c - c0, r - r0)), fill=1)
            for h in p.interiors:
                a = np.asarray(h.coords); hr, hc = xy_to_rc(a[:, 0], a[:, 1])
                if len(a) >= 3: dr.polygon(list(zip(hc - c0, hr - r0)), fill=0)
            m[r0:r1, c0:c1] |= np.array(im, bool)
    return m

LANDG = []
for nm in ("ne_10m_land", "ne_10m_minor_islands"):
    for f in ne(nm)["features"]:
        g = shape(f["geometry"])
        if g.intersects(BB): LANDG += polys_of(g.intersection(BB))
landU = unary_union(LANDG)
LAKEG = []
SKIP_LAKES = {"South Aral Sea", "North Aral Sea"} | set(getattr(IM, "SKIP_LAKES_EXTRA", ()))   # 今日已萎缩的咸海改用历史湖岸；近代形成的湖不画
KEEP_RESERVOIR = {"Lake Zaysan"}
for f in ne("ne_10m_lakes")["features"]:
    if not f["geometry"]: continue
    p = f["properties"]; nm = p.get("name")
    if nm in SKIP_LAKES: continue
    if p.get("featurecla") == "Reservoir" and nm not in KEEP_RESERVOIR: continue
    g = shape(f["geometry"])
    if g.intersects(BB): LAKEG.append((nm, g.intersection(BB)))
for f in ne("ne_10m_lakes_historic")["features"]:
    if not f["geometry"]: continue
    nm = f["properties"].get("name")
    if nm in ("Lop Nur", "Aral Sea"):
        g = shape(f["geometry"])
        if g.intersects(BB): LAKEG.append((nm, g.intersection(BB)))
LAND = rasterize([landU]) & INEXT
WATER = rasterize([g for n, g in LAKEG if g.area > C.BIG_LAKE_AREA])
LAND &= ~WATER
print(f"[{time.time()-T0:.0f}s]", "land cells", int(LAND.sum()))

# ======================================================================
# 4. 通行代价栅格
# ======================================================================
cost = np.ones((NY, NX), np.float64)
# 4a 地形：ETOPO20 起伏与高原
_E = np.loadtxt(gzip.open(C.ETOPO_DIR / "etopo20data.gz"))
_Elon = np.loadtxt(gzip.open(C.ETOPO_DIR / "etopo20lons.gz")); _Elat = np.loadtxt(gzip.open(C.ETOPO_DIR / "etopo20lats.gz"))
_rel = ndimage.maximum_filter(_E, 3) - ndimage.minimum_filter(_E, 3)
_lo2 = np.where(LONC < _Elon[0], LONC + 360, LONC)
_fi = (_lo2 - _Elon[0]) / (_Elon[1] - _Elon[0]); _fj = (LATC - _Elat[0]) / (_Elat[1] - _Elat[0])
ELEV = ndimage.map_coordinates(_E, [_fj, _fi], order=1, mode="nearest")
RELIEF = ndimage.map_coordinates(_rel, [_fj, _fi], order=1, mode="nearest")
cost += C.TERRAIN_RELIEF * np.clip(RELIEF / 1000, 0, 3) + C.TERRAIN_HIGH * np.clip((ELEV - 2500) / 1000, 0, 3)

KM = 6371.0 / C.SCL       # 一个投影单位合多少公里
def wiggle_xy(pts_ll, name, amp_km, wave_km):
    """把手绘脊线加密，并按名字确定的相位做横向摆动（投影平面内）。"""
    ls = LineString(pts_ll)
    n = max(2, int(ls.length / 0.04))
    P = np.array([ls.interpolate(i / n, normalized=True).coords[0] for i in range(n + 1)])
    x, y = fwd(P[:, 0], P[:, 1])
    if amp_km <= 0: return x, y
    dx = np.gradient(x); dy = np.gradient(y); L = np.hypot(dx, dy) + 1e-9
    s = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))] * KM
    h = crc(name); ph1 = (h % 1000) / 1000 * 2 * math.pi; ph2 = (h // 1000 % 1000) / 1000 * 2 * math.pi
    off = (np.sin(2 * math.pi * s / wave_km + ph1) + 0.5 * np.sin(2 * math.pi * s / (wave_km / 2.3) + ph2)) * amp_km / 1.5
    taper = np.minimum(1, np.minimum(s, s[-1] - s) / (wave_km / 2 + 1e-9))   # 两端不摆
    off = off * taper / KM
    return x - dy / L * off, y + dx / L * off

def burn(lines_xy, amp, sig_km):
    if not lines_xy: return 0
    m = np.zeros((NY, NX), bool)
    for x, y in lines_xy:
        ls = LineString(np.column_stack([x, y]))
        n = max(2, int(ls.length / (CELL / 3)))
        P = np.array([ls.interpolate(i / n, normalized=True).coords[0] for i in range(n + 1)])
        r, c = xy_to_rc(P[:, 0], P[:, 1]); r = np.round(r).astype(int); c = np.round(c).astype(int)
        ok = (r >= 0) & (r < NY) & (c >= 0) & (c < NX); m[r[ok], c[ok]] = True
    d = ndimage.distance_transform_edt(~m) * CELL * KM
    return amp * np.exp(-(d / sig_km) ** 2)

cost += burn([wiggle_xy(r[2], r[0], *C.RANGE_WIGGLE) for r in IM.RANGES if r[4]], *C.RANGE_MAJOR)
cost += burn([wiggle_xy(r[2], r[0], *C.RANGE_WIGGLE) for r in IM.RANGES if not r[4]], *C.RANGE_MINOR)
RANGEPOLY, DESERTPOLY = [], {}
for f in ne("ne_10m_geography_regions_polys")["features"]:
    p = f["properties"]
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if not g.intersects(BB): continue
    if p.get("FEATURECLA") == "Range/mtn" and g.area < 60: RANGEPOLY.append(g.intersection(BB))
    if p.get("FEATURECLA") == "Desert": DESERTPOLY[p.get("NAME")] = g
cost += C.RANGE_POLY[0] * ndimage.gaussian_filter(rasterize(RANGEPOLY).astype(np.float32), C.RANGE_POLY[1])

NE_RV = []
for f in ne("ne_10m_rivers_lake_centerlines")["features"]:
    g = f["geometry"]
    if not g: continue
    gg = shape(g)
    if not gg.intersects(BB): continue
    p = f["properties"]
    for ls in lines_of(gg.intersection(EXT_BOX)):
        NE_RV.append((p.get("name"), p.get("scalerank"), ls))
_byamp = {}
for n, sr, ls in NE_RV:
    if n in C.BORDER_RIVERS:
        if n == "Huang": continue
        a = np.asarray(ls.coords); _byamp.setdefault(C.BORDER_RIVERS[n], []).append(fwd(a[:, 0], a[:, 1]))
for mr in IM.MANUAL_RIVERS:
    if mr.get("border"):
        a = np.asarray(mr["pts"]); _byamp.setdefault(tuple(mr["border"]), []).append(fwd(a[:, 0], a[:, 1]))
for (amp, sig), L in sorted(_byamp.items()):
    cost += burn(L, amp, sig)

# 4b 多尺度平滑噪声
rng = np.random.default_rng(C.SEED)
acc = np.zeros((NY, NX), np.float32)
for sg, w in C.NOISE_SCALES:
    n_ = ndimage.gaussian_filter(rng.standard_normal((NY, NX)).astype(np.float32), sg)
    acc += w * n_ / (n_.std() + 1e-9)
acc /= acc.std() + 1e-9
cost *= 1 + C.NOISE_AMP * np.clip(acc, -2, 2) / 2
cost[~LAND] = -1          # 海、大湖与图外：不可通行
print(f"[{time.time()-T0:.0f}s]", "cost built; land cost mean", round(float(cost[LAND].mean()), 2))

# ======================================================================
# 5. 16 邻接多源最短路 → 每格最近的归属点
# ======================================================================
taken = set(); starts = []
for s in SEEDS:   # 吸附到最近的、未被占用的陆地格
    x, y = fwd(s["lon"], s["lat"]); r, c = xy_to_rc(x, y); r, c = int(round(float(r))), int(round(float(c)))
    best = None
    for rad in range(0, 10):
        cands = [(dr * dr + dc * dc, r + dr, c + dc) for dr in range(-rad, rad + 1) for dc in range(-rad, rad + 1)
                 if 0 <= r + dr < NY and 0 <= c + dc < NX and LAND[r + dr, c + dc] and (r + dr, c + dc) not in taken]
        if cands: best = min(cands); break
    if best is None: raise SystemExit("归属点不在陆地上：" + s["id"])
    taken.add((best[1], best[2])); starts.append((best[1], best[2]))
# 只在陆地格上建图：每格 8 个方向（含马步）各一条边，权 = 步长 × 两端代价均值
NL = int(LAND.sum())
nid = np.full((NY, NX), -1, np.int64); nid[LAND] = np.arange(NL)
rows, cols, ws = [], [], []
for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (1, 2), (1, -2), (2, 1), (2, -1)]:
    r0 = slice(0, NY - dr); r1 = slice(dr, NY)
    if dc >= 0: c0 = slice(0, NX - dc); c1 = slice(dc, NX)
    else: c0 = slice(-dc, NX); c1 = slice(0, NX + dc)
    a = nid[r0, c0]; b = nid[r1, c1]; ok = (a >= 0) & (b >= 0)
    w = (0.5 * (cost[r0, c0] + cost[r1, c1]) * math.hypot(dr, dc) * CELL)[ok]
    rows.append(a[ok]); cols.append(b[ok]); ws.append(w)
G = coo_matrix((np.concatenate(ws), (np.concatenate(rows), np.concatenate(cols))), shape=(NL, NL)).tocsr()
del rows, cols, ws
sidx = np.array([nid[r, c] for r, c in starts])
t0 = time.time()
dist, _, src = dijkstra(G, directed=False, indices=sidx, min_only=True, return_predecessors=True)
del G
pos = np.full(NL, -1, np.int32)
okv = src >= 0
seedpos = {int(v): i for i, v in enumerate(sidx)}
srcmap = np.full(NL, -1, np.int32)
for v, i in seedpos.items(): srcmap[v] = i
pos[okv] = srcmap[src[okv]]
LAB = np.full((NY, NX), -1, np.int32); LAB[LAND] = pos
cum = np.full((NY, NX), np.inf); cum[LAND] = dist
print("labelled in", round(time.time() - t0, 1), "s; reached land", int((LAB >= 0).sum()), "/", NL)

# 5b 无主地与外缘
Rs = np.array([C.REACH * s["R"] for s in SEEDS])
inreach = LAND & (LAB >= 0) & (cum <= Rs[np.clip(LAB, 0, None)])
dil = ndimage.distance_transform_edt(~inreach) <= C.CLOSE_RADIUS
closed = (ndimage.distance_transform_edt(dil) > C.CLOSE_RADIUS) & LAND
lbl, nl = ndimage.label(LAND & ~closed)
if nl:
    sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, nl + 1))
    small = np.isin(lbl, np.nonzero(sz < C.HOLE_MAX)[0] + 1)
    closed |= small
owned = (ndimage.gaussian_filter(closed.astype(np.float32), C.EDGE_SIGMA) > 0.5) & LAND
_, (jr, jc) = ndimage.distance_transform_edt(~inreach, return_indices=True)
LABF = np.where(owned, LAB[jr, jc], -1).astype(np.int32)
# 5c 位移场：界线带小弯。先把归属外延入海，免得海岸附近被拉成无主
_, (jr, jc) = ndimage.distance_transform_edt(~(LABF >= 0), return_indices=True)
ext_lab = np.where(LAND, LABF, LABF[jr, jc])
dxw = ndimage.gaussian_filter(rng.standard_normal((NY, NX)).astype(np.float32), C.WARP_SIGMA)
dyw = ndimage.gaussian_filter(rng.standard_normal((NY, NX)).astype(np.float32), C.WARP_SIGMA)
dxw *= C.WARP_AMP / (dxw.std() + 1e-9); dyw *= C.WARP_AMP / (dyw.std() + 1e-9)
RI, CI = np.indices((NY, NX))
wr = np.clip(np.round(RI + dyw).astype(int), 0, NY - 1); wc = np.clip(np.round(CI + dxw).astype(int), 0, NX - 1)
LABW = np.where(LAND & owned, ext_lab[wr, wc], -1).astype(np.int32)
LABW[(LABW < 0) & LAND & owned] = LABF[(LABW < 0) & LAND & owned]
del RI, CI, wr, wc, dxw, dyw, jr, jc
print("owned land", int((LABW >= 0).sum()))

# ======================================================================
# 6. 各节点疆域：共享界线的覆盖图
# ======================================================================
SEA = ~LAND
_, (sjr, sjc) = ndimage.distance_transform_edt(SEA, return_indices=True)   # 海格最近的陆格（不随节点变）
seadist = ndimage.distance_transform_edt(SEA)

def partition(U):
    """U: 每格的单位号（-1 无主陆地，-2 海或图外）。返回平滑后的分类、前两名的平滑值与类别。"""
    classes = sorted(set(np.unique(U).tolist()))
    best1 = np.full((NY, NX), -1.0, np.float32); best2 = np.full((NY, NX), -1.0, np.float32)
    arg1 = np.full((NY, NX), -2, np.int32); arg2 = np.full((NY, NX), -2, np.int32)
    sg = C.SMOOTH_SIGMA; pad = int(4 * sg) + 2
    for k in classes:
        m = U == k
        rows = np.nonzero(m.any(1))[0]; cols = np.nonzero(m.any(0))[0]
        r0, r1 = max(0, rows[0] - pad), min(NY, rows[-1] + pad + 1); c0, c1 = max(0, cols[0] - pad), min(NX, cols[-1] + pad + 1)
        g = ndimage.gaussian_filter(m[r0:r1, c0:c1].astype(np.float32), sg, truncate=3.0)
        B1 = best1[r0:r1, c0:c1]; B2 = best2[r0:r1, c0:c1]; A1 = arg1[r0:r1, c0:c1]; A2 = arg2[r0:r1, c0:c1]
        m1 = g > B1
        m2 = ~m1 & (g > B2)
        B2[m1] = B1[m1]; A2[m1] = A1[m1]; B1[m1] = g[m1]; A1[m1] = k
        B2[m2] = g[m2]; A2[m2] = k
    return arg1, best1, arg2, best2

def boundary_lines(A, B1, A2, B2):
    """在相邻两类平滑值相等处描界：每条格边上插一个点，格角处串起来；交汇点取相邻插值点的均值。"""
    segs = []
    for axis in (1, 0):
        if axis == 1: a, b = A[:, :-1], A[:, 1:]; b1a, b1b = B1[:, :-1], B1[:, 1:]; a2a, a2b = A2[:, :-1], A2[:, 1:]; b2a, b2b = B2[:, :-1], B2[:, 1:]
        else: a, b = A[:-1, :], A[1:, :]; b1a, b1b = B1[:-1, :], B1[1:, :]; a2a, a2b = A2[:-1, :], A2[1:, :]; b2a, b2b = B2[:-1, :], B2[1:, :]
        msk = (a != b) & ((a >= 0) | (b >= 0))
        r, c = np.nonzero(msk)
        # 左（上）格：本类 a 的值 b1a，对方 b 的值（若对方恰是第二名则取之，否则取第二名的值近似）
        da = b1a[r, c] - b2a[r, c]
        db = b1b[r, c] - b2b[r, c]
        t = np.clip(da / (da + db + 1e-9), 0.08, 0.92)
        if axis == 1:
            p0 = np.column_stack([GX0 + (c + 1) * CELL, GY0 + r * CELL]); p1 = np.column_stack([GX0 + (c + 1) * CELL, GY0 + (r + 1) * CELL])
            d = np.column_stack([GX0 + (c + 0.5 + t) * CELL, GY0 + (r + 0.5) * CELL])
        else:
            p0 = np.column_stack([GX0 + c * CELL, GY0 + (r + 1) * CELL]); p1 = np.column_stack([GX0 + (c + 1) * CELL, GY0 + (r + 1) * CELL])
            d = np.column_stack([GX0 + (c + 0.5) * CELL, GY0 + (r + 0.5 + t) * CELL])
        segs.append(np.stack([p0, d, p1], 1))
    S = np.concatenate(segs, 0)
    def ckey(xy): return (int(round((xy[1] - GY0) / CELL)), int(round((xy[0] - GX0) / CELL)))
    ends = np.concatenate([S[:, 0], S[:, 2]], 0)
    er = np.round((ends[:, 1] - GY0) / CELL).astype(np.int64); ec = np.round((ends[:, 0] - GX0) / CELL).astype(np.int64)
    ukeys, cnt = np.unique(er * (NX + 1) + ec, return_counts=True)
    JUNC = set((ukeys[cnt != 2]).tolist())                 # 度数不为 2 的格角：三类以上交汇（或棋盘格）
    isj = lambda xy: (ckey(xy)[0] * (NX + 1) + ckey(xy)[1]) in JUNC
    merged = shapely.line_merge(shapely.multilinestrings(shapely.linestrings(S)))
    chains = [np.asarray(l.coords) for l in lines_of(merged)]
    # 交汇点：链端点（格角）→ 相邻插值点
    jun = {}
    for i, P in enumerate(chains):
        if not isj(P[0]): continue                         # 纯环
        for end, nb in ((0, 1), (-1, -2)):
            jun.setdefault(ckey(P[end]), []).append(P[nb])
    jpos = {k: np.mean(v, 0) for k, v in jun.items()}
    out = []
    for P in chains:
        closed_ = not isj(P[0])
        if closed_:
            Q = P[1:-1:2]                         # 只留插值点（奇数位）
            for _ in range(C.LAPLACE_ROUNDS):
                Q = Q + 0.5 * ((np.roll(Q, 1, 0) + np.roll(Q, -1, 0)) / 2 - Q)
            out.append(np.vstack([Q, Q[:1]]))
        else:
            Q = np.vstack([jpos[ckey(P[0])], P[1:-1:2], jpos[ckey(P[-1])]])
            for _ in range(C.LAPLACE_ROUNDS):
                Q[1:-1] = Q[1:-1] + 0.5 * ((Q[:-2] + Q[2:]) / 2 - Q[1:-1])
            out.append(Q)
    return out

def cover(A, lines, keys):
    """把界线网络围成面，按栅格分类归到各单位；返回 {单位: 经纬度多边形}（已整体简化）。"""
    noded = shapely.node(MultiLineString([LineString(q) for q in lines]))
    faces = [p for p in polys_of(shapely.polygonize(lines_of(noded))) if p.area > 0]
    pts = shapely.point_on_surface(faces)
    fx, fy = shapely.get_x(pts), shapely.get_y(pts)
    r = np.clip(np.floor((fy - GY0) / CELL).astype(int), 0, NY - 1); c = np.clip(np.floor((fx - GX0) / CELL).astype(int), 0, NX - 1)
    cls = A[r, c]
    groups = {}
    for f, k in zip(faces, cls.tolist()):
        if k >= 0: groups.setdefault(k, []).append(f)
    ks = [k for k in keys if k in groups]
    geoms = []
    for k in ks:
        try: g = shapely.coverage_union_all(groups[k])
        except Exception: g = unary_union(groups[k])
        geoms.append(to_ll(shapely.make_valid(g)))
    simp = shapely.coverage_simplify(np.array(geoms, dtype=object), C.SIMPLIFY_TERR, simplify_boundary=True) if geoms else []
    res = {}
    for k, g in zip(ks, simp):
        parts = []
        for p in polys_of(shapely.make_valid(g)):
            if p.area < C.MIN_PART_AREA: continue
            holes = [h for h in p.interiors if Polygon(h).area >= C.MIN_PART_AREA]
            parts.append(Polygon(p.exterior, holes))
        if parts: res[k] = MultiPolygon(parts)
    return res

def rings_of(mp):
    out = []
    for p in polys_of(mp):
        out.append(enc_ring(list(p.exterior.coords)))
        out += [enc_ring(list(h.coords)) for h in p.interiors]
    return out

def anchor(mask):
    """注记点：最大陆块的不可达极点。返回 [经, 纬, 面积(平方度), 内切半径(度)]。"""
    ml = mask & LAND
    if not ml.any(): ml = mask
    lab, n = ndimage.label(ml)
    sizes = ndimage.sum(ml, lab, range(1, n + 1))
    big = lab == (int(np.argmax(sizes)) + 1)
    rows = np.nonzero(big.any(1))[0]; cols = np.nonzero(big.any(0))[0]
    sub = big[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
    dt = ndimage.distance_transform_edt(np.pad(sub, 1))[1:-1, 1:-1]
    r, c = np.unravel_index(np.argmax(dt), dt.shape)
    lo, la = rc_to_ll(r + rows[0], c + cols[0])
    k = CELL / DEG
    return [round(float(lo), 2), round(float(la), 2), round(float(ml.sum()) * k * k, 2), round(float(dt[r, c]) * k, 2)]

ADJ_Z, ADJ_P = set(), set()
def adj_pairs(own, S):
    for a, b in [(own[:, :-1], own[:, 1:]), (own[:-1, :], own[1:, :])]:
        m = (a != b) & (a >= 0) & (b >= 0)
        if m.any():
            pr = np.unique(np.stack([np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], 1), axis=0)
            S.update(map(tuple, pr.tolist()))

POOL, POOLIX = [], {}
def pooled(rings):
    key = json.dumps(rings, separators=(",", ":"))
    if key not in POOLIX: POOLIX[key] = len(POOL); POOL.append(rings)
    return POOLIX[key]

OUTSN = []
for sn in SNAPS:
    st = sn["st"]
    own_seed = np.full(len(SEEDS), -1, np.int32)
    for sid, uk in st["own"].items():
        if uk is not None: own_seed[SID[sid]] = UK[uk]
    U = np.where(LABW >= 0, own_seed[np.clip(LABW, 0, None)], -1).astype(np.int32)
    U[~LAND] = -2
    fill = SEA & (seadist <= C.SEA_FILL_CELLS) & INEXT
    U[fill] = U[sjr[fill], sjc[fill]]
    U[fill & (U == -1)] = -2
    present = sorted(set(own_seed[own_seed >= 0].tolist()))
    polmap = {u: UK[pol_of(st, UNITS[u]["k"])] for u in present}
    A, B1, A2, B2 = partition(U)
    PR = A.copy()
    for u, p in polmap.items(): PR[A == u] = p
    adj_pairs(np.where(LAND, A, -1), ADJ_Z); adj_pairs(np.where(LAND, PR, -1), ADJ_P)
    zpoly = cover(A, boundary_lines(A, B1, A2, B2), present)
    multi = sorted({p for u, p in polmap.items() if p != u or list(polmap.values()).count(p) > 1})
    ppoly = {}
    for p in multi:
        mem = [zpoly[u] for u in present if polmap[u] == p and u in zpoly]
        if mem:
            try: ppoly[p] = shapely.coverage_union_all(mem)
            except Exception: ppoly[p] = unary_union(mem)
    z = {str(k): pooled(rings_of(v)) for k, v in zpoly.items()}
    p_ = {str(k): pooled(rings_of(v)) for k, v in ppoly.items()}
    lz = {str(u): anchor(A == u) for u in present if (A == u).any()}
    lp = {str(p): anchor(PR == p) for p in multi if (PR == p).any()}
    OUTSN.append(dict(y=sn["y"], era=sn["era"], t=sn["t"], d=sn["d"], z=z, lz=lz, p=p_, lp=lp,
             own=own_seed.tolist(),
             pol={str(u): p for u, p in polmap.items()},
             lab={str(UK[k]): v for k, v in sorted(st["lab"].items()) if UK[k] in polmap or UK[k] in polmap.values()},
             seat={str(UK[k]): SID[v] for k, v in sorted(st["seat"].items()) if UK[k] in polmap},
             h=sorted(UK[k] for k in st["hatch"] if UK[k] in polmap)))
    print("snap", sn["y"], "units", len(present), "polities", len(set(polmap.values())), "faces→units", len(zpoly), flush=True)
print("pool", len(POOL))

# ======================================================================
# 7. 配色：低饱和度，相邻单位尽量区分（OKLCH 空间贪心着色）
# ======================================================================
def oklch_to_rgb(L, Cc, h):
    a = Cc * math.cos(math.radians(h)); b = Cc * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    def gam(x):
        x = max(0, min(1, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return "#%02X%02X%02X" % tuple(int(round(gam(v) * 255)) for v in (r, g, bb))
def rgb_to_oklab(hx):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(hx[i:i + 2], 16)) for i in (1, 3, 5))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.array([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s])
PAL = [(L, Cc, (i * C.PALETTE_HUE_STEP + off) % 360) for L, Cc, off in C.PALETTE_LEVELS for i in range(360 // C.PALETTE_HUE_STEP)]
def lab_of_pal(p):
    L, Cc, h = p
    return np.array([L, Cc * math.cos(math.radians(h)), Cc * math.sin(math.radians(h))])
PL = [lab_of_pal(p) for p in PAL]
nbr = {i: set() for i in range(len(UNITS))}
for a, b in sorted(ADJ_Z | ADJ_P):
    nbr[a].add(b); nbr[b].add(a)
LIGHT, DARK, LABV = {}, {}, {}
for k, (lh, dh) in C.PRESET_HEX.items():
    if k in UK: u = UK[k]; LIGHT[u], DARK[u], LABV[u] = lh, dh, rgb_to_oklab(lh)
for k, v in C.PRESET_COLORS.items():
    if k in UK and UK[k] not in LIGHT:
        u = UK[k]; L, Cc, h = v
        LIGHT[u] = oklch_to_rgb(L, Cc, h); DARK[u] = oklch_to_rgb(min(C.DARK_L_MAX, L + C.DARK_L_LIFT), Cc + C.DARK_C_LIFT, h); LABV[u] = lab_of_pal(v)
usage = {}
for u in sorted(range(len(UNITS)), key=lambda u: (-len(nbr[u]), u)):   # 邻居多的先挑
    if u in LIGHT: continue
    pref = UNITS[u].get("like")       # 可指定“像某单位”：同色相附近挑
    best, bs = None, -1e9
    for j, p in enumerate(PAL):
        dmin = min([np.linalg.norm(PL[j] - LABV[n]) for n in nbr[u] if n in LABV] + [1.0])
        score = dmin - C.REUSE_PENALTY * usage.get(j, 0)
        if pref and pref in UK and UK[pref] in LABV: score -= 0.6 * np.linalg.norm(PL[j] - LABV[UK[pref]])
        if score > bs: bs, best = score, j
    L, Cc, h = PAL[best]; usage[best] = usage.get(best, 0) + 1
    LIGHT[u] = oklch_to_rgb(L, Cc, h); DARK[u] = oklch_to_rgb(min(C.DARK_L_MAX, L + C.DARK_L_LIFT), Cc + C.DARK_C_LIFT, h); LABV[u] = PL[best]
mind = min([np.linalg.norm(LABV[a] - LABV[b]) for a, b in ADJ_Z if a in LABV and b in LABV] or [0])
print("min neighbour colour distance", round(float(mind), 3))

# ======================================================================
# 8. 底图要素与条目
# ======================================================================
LAND_OUT = []
for p in polys_of(landU.intersection(box(LON0 - 0.5, LAT0 - 0.5, LON1 + 0.5, LAT1 + 0.5))):
    p = p.simplify(C.SIMPLIFY_LAND)
    if p.is_empty or p.area < C.LAND_MIN_AREA: continue
    for q in polys_of(p):
        rings = [enc_ring(list(q.exterior.coords))] + [enc_ring(list(h.coords)) for h in q.interiors if Polygon(h).area > C.LAND_HOLE_MIN_AREA]
        LAND_OUT.append(rings)
print("land polys", len(LAND_OUT))

# 今国界：由中国视角版国界多边形求相邻边（海岸线不画）
CTRY = [shape(f["geometry"]) for f in ne("ne_10m_admin_0_countries_chn")["features"] if f["geometry"]]
CTRY = [g.intersection(BB) for g in CTRY if g.intersects(BB)]
coastbuf = landU.boundary.buffer(0.03)
BORDER = []
_bl = unary_union([g.boundary for g in CTRY]).difference(coastbuf).intersection(EXT_BOX)
for ls in lines_of(shapely.line_merge(_bl) if not _bl.is_empty else _bl):
    ls = ls.simplify(C.SIMPLIFY_BORDER)
    if ls.length > 0.08: BORDER.append(enc_ring(list(ls.coords)))
print("border lines", len(BORDER))

PROV = json.load(open(C.PROV_JSON, encoding="utf8"))

ITEMS = []
def add_item(d): d["i"] = len(ITEMS); ITEMS.append(d); return d["i"]

# 河流：Natural Earth 河道 + 手绘古河道，按古名合并为条目
RIVERS = []
river_item = {}
def river_key(n, xs, ys):
    return IM.river_alias(n, xs, ys) if hasattr(IM, "river_alias") else n
for n, sr, ls in NE_RV:
    pts = list(ls.simplify(C.SIMPLIFY_RIVER).coords)
    if len(pts) < 2: continue
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    name = river_key(n, xs, ys)
    if name is False: continue                       # 别名函数可以把今河道整段剔除
    info = IM.NE_RIVERS.get(name)
    kind = "faint"
    if sr is not None and sr <= 6: kind = "minor"
    if info: kind = "major" if info[3] else "minor"
    if name in IM.MODERN_SPLIT:                       # 今河道与古河道分叉处：一侧照画，一侧改虚线
        cut = IM.MODERN_SPLIT[name]
        keep = [(x, y) for x, y in pts if cut(x, y)]
        mod_ = [(x, y) for x, y in pts if not cut(x, y)]
        if len(keep) > 1: RIVERS.append(dict(k=kind, p=enc_ring(keep), nm=info[0] if info else None, info=info))
        if len(mod_) > 1: RIVERS.append(dict(k="modern", p=enc_ring(mod_), nm=None))
        continue
    if sr is not None and sr > C.RIVER_MAX_SCALERANK and not info: continue
    RIVERS.append(dict(k=kind, p=enc_ring(pts), nm=(info[0] if info else None), info=info))
for mr in IM.MANUAL_RIVERS:
    RIVERS.append(dict(k="major" if mr["major"] else "minor", p=enc_ring(mr["pts"]), nm=mr["nm"],
                       info=(mr["nm"], mr["mod"], mr["note"], mr["major"]), y0=mr.get("y0"), y1=mr.get("y1"), key=mr.get("key", mr["nm"])))
for r in RIVERS:
    if not r.get("nm"): r["it"] = None; continue
    info = r["info"]; key = r.get("key") or r["nm"]
    if key not in river_item:
        ov = IM.RIVER_ITEM_OVERRIDE.get(key, {})
        river_item[key] = add_item(dict(c="river", sub="river", old=ov.get("old", info[0]), mod=ov.get("mod", info[1]),
                                        note=ov.get("note", info[2]), major=bool(info[3])))
    r["it"] = river_item[key]
seglen = {}
for r in RIVERS:
    if r.get("it") is None: continue
    x = y = 0; pts = []
    for i in range(0, len(r["p"]), 2): x += r["p"][i]; y += r["p"][i + 1]; pts.append((x / 100, y / 100))
    if len(pts) < 2: continue
    L = LineString(pts).length
    if L > seglen.get(r["it"], (0, None))[0]:
        mid = LineString(pts).interpolate(0.5, normalized=True)
        seglen[r["it"]] = (L, [round(mid.x, 3), round(mid.y, 3)])
for it, (L, a) in seglen.items(): ITEMS[it]["anc"] = a
RIV_OUT = []
for r in RIVERS:
    d = dict(k=r["k"], p=r["p"])
    if r.get("it") is not None: d["it"] = r["it"]
    if r.get("y0") is not None: d["y0"] = r["y0"]
    if r.get("y1") is not None: d["y1"] = r["y1"]
    RIV_OUT.append(d)
print("rivers", len(RIV_OUT), "named", len(river_item))

LAKES = []
for n, g in LAKEG:
    info = IM.NE_LAKES.get(n)
    if not info and g.area < 0.03: continue
    for p in polys_of(g.simplify(C.SIMPLIFY_LAKE)):
        if p.area < 0.004: continue
        it = None
        if info:
            ex = [x for x in ITEMS if x["c"] == "river" and x.get("sub") == "lake" and x["old"] == info[0] and x["mod"] == info[1]]
            if ex: it = ex[0]["i"]
            else:
                c = p.representative_point()
                it = add_item(dict(c="river", sub="lake", old=info[0], mod=info[1], note=info[2], anc=[round(c.x, 2), round(c.y, 2)]))
        LAKES.append(dict(r=enc_ring(list(p.exterior.coords)), **({"it": it} if it is not None else {})))
for nm, mod, lo, la, rx, ry, note in IM.MARSHES:
    add_item(dict(c="river", sub="marsh", old=nm, mod=mod, note=note, lon=lo, lat=la, rx=rx, ry=ry, anc=[lo, la]))
CAN = []
for cn in IM.CANALS:
    nm, mod, pts, note = cn[:4]
    it = add_item(dict(c="canal", old=nm, mod=mod, note=note, anc=list(LineString(pts).interpolate(0.5, normalized=True).coords[0])))
    CAN.append(dict(p=enc_ring(pts), it=it))
for nm, mod, pts, note, major in IM.RANGES:
    a = LineString(pts).interpolate(0.5, normalized=True)
    add_item(dict(c="range", old=nm, mod=mod, note=note, geo=pts, anc=[round(a.x, 3), round(a.y, 3)], major=bool(major)))
DES = []
for nm, mod, nename, note in IM.DESERTS:
    g = DESERTPOLY.get(nename)
    if g is None: print("  没找到荒漠", nename); continue
    g = g.intersection(EXT_BOX)
    c = g.representative_point()
    it = add_item(dict(c="desert", old=nm, mod=mod, note=note, anc=[round(c.x, 2), round(c.y, 2)]))
    for p in polys_of(g.simplify(0.05)):
        DES.append(dict(r=enc_ring(list(p.exterior.coords)), it=it))

for nm, mod, lo, la, st, yrs, note, at in IM.CAPITALS:
    assert st in UK, ("都城所属政权不存在", st)
    if at: assert at in SID, ("都城关联的归属点不存在", at)
    add_item(dict(c="capital", old=nm, mod=mod, lon=lo, lat=la, st=UK[st], yrs=yrs, note=note, at=SID.get(at) if at else None))
for nm, mod, lo, la, y, yt, sides, cmd, note in IM.BATTLES:
    add_item(dict(c="battle", old=nm, mod=mod, lon=lo, lat=la, y=y, yt=yt, sides=sides, cmd=cmd, note=note))
for nm, mod, lo, la, note in IM.PASSES:
    add_item(dict(c="pass", old=nm, mod=mod, lon=lo, lat=la, note=note))
EVENT_END = getattr(IM, "EVENT_END", {})
for nm, mod, lo, la, y, yt, note in IM.EVENTS:
    d = dict(c="event", old=nm, mod=mod, lon=lo, lat=la, y=y, yt=yt, note=note)
    if nm in EVENT_END: d["y1"] = EVENT_END[nm]
    add_item(d)
for nm, lo, la, y0, y1, note in IM.PEOPLES:
    add_item(dict(c="people", old=nm, mod="", lon=lo, lat=la, y0=y0, y1=y1, note=note))
for it in ITEMS:
    if "lon" in it: assert LON0 <= it["lon"] <= LON1 and LAT0 <= it["lat"] <= LAT1, ("条目在全图范围外", it["old"])

# 行军路线：每条一组 [经, 纬, 到达年, 地名]，前端按节点年份画出已走过的一段
ROUTES = []
for R in getattr(IM, "ROUTES", []):
    pts = [list(p) for p in R["pts"]]
    it = add_item(dict(c="route", old=R["name"], mod=R["mod"], note=R["note"], y=pts[0][2], y1=pts[-1][2],
                       yt=R.get("yt", f"{pts[0][2]}—{pts[-1][2]}"), anc=pts[len(pts) // 2][:2]))
    ROUTES.append(dict(it=it, pts=pts))

# 重要地域（燕云十六州）：由成员州的栅格并集描出范围线，分区之间画分界线
from scipy.ndimage import map_coordinates
def contours_ll(field, level=0.5):
    out = []
    for cnt in measure.find_contours(field, level):
        lo, la = rc_to_ll(cnt[:, 0], cnt[:, 1])
        out.append(np.column_stack([lo, la]))
    return out
REG_OUT = []
for R in getattr(IM, "REGIONS", []):
    ids = lambda names: [SID[n] for n in names]
    for n in R["members"] + R.get("extra", []): assert n in SID, ("地域成员不在 seeds.txt", n)
    allm = np.isin(LABW, ids(R["members"] + R.get("extra", [])))
    su = ndimage.gaussian_filter(allm.astype(np.float32), C.SMOOTH_SIGMA * 1.5)
    rings = []
    for P in contours_ll(np.pad(su, 1)[1:-1, 1:-1]):
        ls = LineString(P).simplify(C.SIMPLIFY_TERR)
        if len(ls.coords) >= 4 and Polygon(ls.coords).area > C.MIN_PART_AREA: rings.append(enc_ring(list(ls.coords)))
    rlab = anchor(allm)
    groups = []
    for g in R.get("groups", []):
        gm = np.isin(LABW, ids(g["members"] + g.get("extra", [])))
        glab = anchor(gm)
        # 分区注记避开地域总名
        lo0, la0 = rlab[0], rlab[1]
        near = np.hypot((LONC - lo0) * math.cos(math.radians(la0)), LATC - la0) < 1.2
        ml = gm & LAND & ~near
        if ml.any():
            glab = anchor(ml)
        lines = []
        if g.get("line"):
            sg = ndimage.gaussian_filter(gm.astype(np.float32), C.SMOOTH_SIGMA * 1.5)
            for cnt in measure.find_contours(sg, 0.5):
                inside = map_coordinates(su, cnt.T, order=1) > 0.8
                run = []
                for (r, c), ok in zip(cnt, inside):
                    if ok: run.append((r, c))
                    elif run:
                        if len(run) > 3: lines.append(run)
                        run = []
                if len(run) > 3: lines.append(run)
            enc = []
            for l in lines:
                l = np.array(l); lo, la = rc_to_ll(l[:, 0], l[:, 1])
                enc.append(enc_ring(list(LineString(np.column_stack([lo, la])).simplify(C.SIMPLIFY_TERR).coords)))
            lines = enc
        groups.append(dict(n=g["name"], y0=g.get("y0", R["y0"]), lab=glab, lines=lines))
    it = add_item(dict(c="region", old=R["name"], mod=R["mod"], note=R["note"], tag=R.get("tag", ""), y0=R["y0"], y1=R.get("y1", 9999),
                       members=ids(R["members"]), anc=rlab[:2], lab=rlab))
    REG_OUT.append(dict(it=it, y0=R["y0"], y1=R.get("y1", 9999), rings=rings, groups=groups))
print("regions", [(ITEMS[r["it"]]["old"], len(r["rings"])) for r in REG_OUT])

# ======================================================================
# 输出
# ======================================================================
SEAS = [[n, lo, la, lv] for n, lo, la, lv in getattr(IM, "SEAS", [])]
GEO = dict(land=LAND_OUT, prov=PROV, border=BORDER, rivers=RIV_OUT, lakes=LAKES, canals=CAN, deserts=DES,
           pool=POOL, snaps=OUTSN, regions=REG_OUT, routes=ROUTES, seas=SEAS, ext=[LON0, LON1, LAT0, LAT1], proj=list(C.PROJ))
UOUT = [dict(k=u["k"], n=u["n"], kind=u["kind"], note=u["note"], cl=LIGHT[i], cd=DARK[i]) for i, u in enumerate(UNITS)]
SOUT = [dict(id=s["id"], n=s["n"], mod=s["mod"], lon=s["lon"], lat=s["lat"], t=s["t"], **({"nm": s["names"]} if s["names"] else {})) for s in SEEDS]
DATA = dict(units=UOUT, seeds=SOUT, items=ITEMS)
C.BUILD.mkdir(exist_ok=True)
json.dump(GEO, open(C.BUILD / "geo.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(DATA, open(C.BUILD / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
np.save(C.BUILD / "label.npy", LABW)   # 每个格子归哪个点，供调试
print("geo.json", (C.BUILD / "geo.json").stat().st_size // 1024, "KB; data.json", (C.BUILD / "data.json").stat().st_size // 1024, "KB")
