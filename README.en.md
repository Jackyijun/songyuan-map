# Song, Liao, Xia, Jin and Yuan, 979–1279

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

An interactive historical map of East Asia and Eurasia from the Song reunification to the fall of the Song at Yamen (979–1279), in Chinese and English: the territories of states, circuits, uluses and provinces at 61 snapshots, with historical and modern names for 640 prefectures and towns, from central Europe and Egypt in the west to Japan in the east. It also shows 99 capitals, 145 battles, 15 campaign routes, 30 passes, 58 events, 70 mountain ranges, more than a hundred rivers and lakes, the Sixteen Prefectures of Yan and Yun, and the peoples on the periphery.

It continues the *Tang–Song transition* map (755–979): the colors of the states at the 979 snapshot match the last snapshot of that map.

## 1. Just look

Double-click **`docs/index.html`** and open it in any modern browser (Chrome, Edge, Safari, Firefox).

The file is about 4 MB with all data, styles and scripts embedded: no network, no server and no external libraries. You can copy it to a USB stick, send it to someone, or put it on your own website.

- Timeline: click a tick to jump; ▶ on the left plays, 1× / 2× below it changes speed; the ← → keys step through snapshots.
- Coloring: the "Circuits & uluses / States" switch in the top bar. In "Circuits & uluses" mode Song and Jin are divided into circuits, Liao into its five capital circuits, the Mongol Empire into uluses and the Yuan into provinces; after 1260 the four khanates are states of their own.
- Hatching: vassals and tributaries (for example the Zubu, Shiwei and Jurchen tribes under Liao; the Kara-Khanids and Khwarazm under the Western Liao; Western Xia, Goryeo, Rum, Cilician Armenia and the Rus' principalities under the Mongols). In "States" mode they take their overlord's color but keep their hatching, name and thin dashed outline.
- View: the drop-down in the top bar offers the whole map, the Mongol Empire and 16 regions.
- Language: the "中 | EN" switch at the top right of the map (at the top right of the content in the Timeline and Gazetteer views); the choice is remembered by the browser, and adding `#en` to the URL opens the English version directly. In English the map labels are in English only, while tooltips, the index, the timeline and the gazetteer add the original Chinese characters after each English name. Search works in both languages, and English searches ignore diacritics.

## 2. Live site

https://jackyijun.github.io/songyuan-map/

## 3. Build locally

You only need to rebuild after changing the historical content (`content/`) or the parameters (`src/config.py`). You need **Python 3.10 or newer** and at least 4 GB of memory.

**macOS / Linux**

```bash
cd songyuan-map
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py --open
```

**Windows (PowerShell)**

```powershell
cd songyuan-map
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py --open
```

A full build takes about 15–20 minutes (a grid of over two million cells, 61 snapshots); then open the newly built `docs/index.html` in a browser.

| Command | What it does |
|---|---|
| `python run.py` | Download the base data if missing → compute the territories → assemble the HTML |
| `python run.py --html` | Only reassemble the HTML (when you changed only `src/template.html`; a few seconds) |
| `python run.py --open` | Open the result in a browser when done |
| `python run.py --html --draft` | Build even if English text is missing or out of date (missing text temporarily shows the Chinese); without `--draft` the build stops with an error |
| `python tools/i18n.py status` | State of the English version: how many entries are missing, out of date or not yet fingerprinted (see section 7) |
| `python run.py --preview 1141,1279` | Also draw territory sketches of these snapshots to `build/preview-*.png` |
| `python tools/preview.py 1227 --box 100,112,34,42` | Draw sketches only, optionally for a bounding box (west,east,south,north) and with `--mode zhen` |
| `python tools/screenshot.py` | (Optional, needs Playwright) take headless-browser screenshots and check for script errors |

The archive includes the base data (`geodata/`, about 43 MB), so you can build offline; if you delete it, `run.py` downloads pinned versions from GitHub (the ETOPO relief is also checked against its sha256).

In the same environment the same input always builds byte-for-byte the same output, so changes can be tracked safely with git.

After building, commit `docs/index.html` and push it to `main`; the live site updates automatically.

## 4. Directory layout

```
songyuan-map/
├── run.py                 one-step build entry point
├── requirements.txt
├── README.md              this guide in Chinese (shown by default on GitHub)
├── README.en.md           this guide in English
├── docs/
│   ├── index.html         ★ the result, a single file (GitHub Pages publishes from /docs)
│   └── .nojekyll
├── content/               ★ historical content (hand-written; most edits happen here)
│   ├── seeds.txt          787 points (347 prefectures, 293 towns, 147 helper points): historical names, coordinates, modern locations, name changes
│   ├── snaps.txt          61 snapshots: which unit and which state each point belongs to in that year
│   ├── units.py           names and descriptions of 179 states, circuits, khanates and tribes
│   ├── items.py           capitals, battles, passes, events, peoples
│   ├── items_geo.py       mountains, rivers, lakes, canals, deserts, seas, the Sixteen Prefectures, campaign routes
│   └── en/                ★ English version: translations (JSON) matching the files above, zh.lock.json fingerprints, GLOSSARY.md naming conventions
├── src/
│   ├── config.py          ★ all paths and tunable parameters (grid, costs, smoothing, colors…)
│   ├── fetch_data.py      download pinned base data if missing
│   ├── build.py           compute territories; writes build/geo.json and build/data.json
│   ├── assemble.py        merge in the English, check for missing text, inject the data into the template; writes docs/index.html
│   ├── i18n.py            English version: list what needs translating, check for missing and out-of-date text, merge translations into the data
│   └── template.html      front end: page structure, styles, interaction script
├── geodata/
│   ├── prov.json          modern Chinese provincial borders (simplified)
│   ├── ne/                Natural Earth 1:10m GeoJSON
│   └── etopo/             ETOPO20 global relief
├── tools/
│   ├── i18n.py            English maintenance: status / todo / lock / table
│   ├── preview.py         matplotlib territory sketches
│   └── screenshot.py      Playwright screenshot check
└── build/                 intermediate files (safe to delete)
```

## 5. How it works

```
content/ ──────┐
               ├─► build.py ─► build/geo.json + data.json ─► assemble.py ─► docs/index.html
geodata/ ──────┘                                               ▲
                                                 src/template.html
```

### Why the territories are computed

What the histories can tell us is that "in a given year a given prefecture belonged to a given state and circuit"; they seldom give continuous boundary lines. So only the allegiance **point → unit → state** is written by hand (`snaps.txt`), and a "travel cost" map lets the computer work out the boundaries between points, making them follow ridges and great rivers wherever possible.

### What `build.py` does

1. **Read the points**: `seeds.txt`. Type `z` is a prefecture, `c` a town or a place outside China, `r` a helper point that only claims territory and is not shown on the map.
2. **Parse the snapshots**: `snaps.txt` is a small declarative language (syntax below). Each `@year` block inherits all the allegiances of the previous snapshot and only states what changed.
3. **Grid on the projected plane**: project first (Albers equal-area conic, standard parallels 25°N and 47°N, origin 38°N 95°E), then cut an equal-spaced grid on the projected plane (about 7 km per cell) from 14°E to 146°E and 10°N to 62°N. Lakes larger than 0.15 square degrees count as water; the Aral Sea uses its historical shoreline; modern reservoirs and lakes formed in modern times are not drawn.
4. **Cost grid**: each cell has a base cost of 1, plus:
   - ETOPO20 relief and plateaus above 2,500 m;
   - the mountain ranges in `items_geo.RANGES`, which "burn" a Gaussian band of high cost along their ridgelines (peak +8 for main ranges, +3.5 for minor ones), the ridgelines first given a little lateral wobble;
   - a small extra cost over Natural Earth's mountain polygons;
   - border rivers (Yangtze, Huai, Han, Amu Darya, Syr Darya, Danube, Volga, Euphrates… plus the hand-drawn old lower Huai and the Song–Liao border river, the Baigou);
   - finally a ±38% multi-scale smooth noise, so that boundaries on the plains also wind naturally.
5. **Multi-source shortest paths**: with all points as sources, one run of `scipy.sparse.csgraph.dijkstra(min_only=True)` on a 16-neighbor land grid (including knight moves) assigns each cell to the point with the lowest cost distance. Cells beyond reach are unclaimed; the outer edges get a morphological closing, small holes filled, Gaussian smoothing, and a smooth displacement field on top.
6. **Polygons**: for each snapshot, the cells are grouped by allegiance and shared boundaries are traced where the smoothed values of two neighboring groups are equal (junctions of three or more take the mean of the intersections); every boundary is traced once and shared by both sides, then given three rounds of Laplacian smoothing. Shapely's `polygonize` assembles them into a coverage, simplified as a whole with `coverage_simplify`. State and unit borders are built from the same shared edges, so there are no gaps or overlaps. Geometry that does not change between snapshots is stored only once (`GEO.pool`).
7. **Colors**: states continuing from the Tang–Song map keep that map's colors (`PRESET_HEX`); Jin, the Mongols, the Western Liao, Khwarazm, the Seljuks, Byzantium and the four khanates have fixed hues (`PRESET_COLORS`); the rest are colored greedily from a low-chroma OKLCH palette according to their adjacency across all snapshots. The dark theme lightens them all.
8. **Base map and items**: coasts, modern borders, lakes and deserts come from Natural Earth. The base map extends far beyond the territories, to `BASE_EXTENT` (25°W to 180°E, 11°S to 82°N); land outside the territory extent gets a thin paper-colored veil, and the extent is marked with a dashed line. Rivers are mapped to their historical names through `NE_RIVERS` (Huang → 河, Amu Darya → 阿母河, Volga → 亦的勒河…). The lower Yellow River is drawn in three courses by date: the old Jingdong channel (until 1048), the northern course (1048–1128) and the southern course into the Huai (after 1128); the modern river east of Zhengzhou is drawn dashed.

### The front end (`src/template.html`)

- **No dependencies**: plain JavaScript and SVG.
- **Layers (bottom to top)**: land → desert stipple → territory fill → vassal hatching → heavy state borders → the Sixteen Prefectures → lakes → modern provinces → modern borders → mountains → rivers → canals → veil and dashed line outside the territory extent → campaign routes, symbols and labels.
- **Time**: each snapshot covers the years after the previous snapshot up to its own year. Battles, events and campaign routes are shown only for the current period; the stretch of a route covered in this period is drawn solid with arrows, earlier stretches dashed. Clicking an item from another period in the index or timeline moves the timeline there.
- **Capitals**: only current capitals (solid squares) and former capitals (dashed squares) are shown.
- **Themes**: all colors are CSS variables and follow the system's light or dark theme; each unit's color is `--u-<index>`, injected by `assemble.py`.
- **Language**: every piece of text is taken in the current language through a few accessor functions (`LZ(zh, en)`, `iF(item, field)` and others), and switching redraws the map, index, timeline and gazetteer. English labels are measured on a canvas for collision avoidance, and long names that do not fit inside a territory wrap onto two lines.

### `assemble.py`

The template has four placeholders: `__GEO__`, `__DATA__`, `__UCSS_LIGHT__` and `__UCSS_DARK__`. The script first uses `src/i18n.py` to check that the English is complete and up to date (stopping with an error if not, unless `--draft` is given), then merges the English into the data (units `ne`/`se`/`notee`, points `ne`/`nme`/`mode`, items `e`, snapshots `erae`/`te`/`de`/`labe`), replaces the placeholders, and wraps the result in the `<!doctype html>` document shell.

## 6. Common changes

**Change where a place belongs in a given year**: add a line in that year's block of `snaps.txt`, e.g. to give Haizhou to Jin in 1141:

```
山东东路: 海州
```

**Add a point**: add a line `ID longitude latitude modern-location [type] [N=year:name,…]` to `seeds.txt`, assign it to a unit in the first snapshot of `snaps.txt` (or the one where it appears), and check with `python run.py --preview year`.

**Rename a place**: add `N=0:old-name,year:new-name` to its line in `seeds.txt`, e.g. `N=0:杭州,1129:临安府`.

**Add a snapshot**: insert `@year | reign era | title | description` between two snapshots in `snaps.txt` and write what changed that year relative to the previous one. The front end adds a tick automatically.

**Add a battle, pass, event or capital**: add a tuple in the same format to `items.py`. Battles and events are assigned to snapshots by year automatically; events lasting several years get an end year in `EVENT_END`.

**Add a campaign route**: add one to `items_geo.ROUTES`, writing each point of `pts` as `[longitude, latitude, year reached, place name]`.

**Add a state, circuit or tribe**: add `S(...)` (state), `Z(...)` (subdivision) or `T(...)` (tribe) to `units.py` and use its key in `snaps.txt`.

**Stop a border from crossing a mountain range**: add the range's ridgeline coordinates to `items_geo.RANGES`, with `1` as the last field (main range, higher cost).

**Change only the page's look or interaction**: edit `src/template.html`, then run `python run.py --html`.

**Added or changed any Chinese text** (points, items, units, snapshot descriptions…): add or update the English in `content/en/` at the same time, or the strict build will report missing or out-of-date text; see section 7.

### `snaps.txt` syntax

```
@year | era | title | description               start a snapshot (inherits the previous one)
unit: point point point                         assign these points to the unit
unit[label]{seat}>state: point …                also set this period's label, seat and overlord (all optional)
unit[]:                                         clear the label, reverting to the name in units.py
unit: @other-unit                               take over every point that belonged to other-unit at the start of this snapshot
unit: @other-unit@year                          take over the points that belonged to other-unit at the end of that year's snapshot
·: point point                                  make unclaimed
藩属: unit unit …                               this period's vassals and tributaries (hatched on the map), replacing the previous list
+藩属: unit / -藩属: unit                        add to or remove from the previous list
# comment
```

If the state is omitted, the default from `units.py` is used. A label, seat or overlord, once set, carries over to later snapshots until it is changed again.

## 7. The English version

Chinese is the source text; the English is kept under the same keys in `content/en/`:

| File | Contents | Key |
|---|---|---|
| `units.json` | states, circuits, khanates, tribes: full name `n`, short map name `s`, description `note` | unit key (e.g. `宋`) |
| `labels.json` | period labels from snapshots (the `[label]` in `snaps.txt`) | Chinese label |
| `seeds.json` | prefectures and towns: modern location `mod`, names in each period `n` | point ID |
| `items.json` | items: `old` `mod` `note` `yt` `sides` `cmd` `tag`, region subdivisions `g`, route place names `p` | `category:historical-name` (e.g. `battle:高梁河之战`) |
| `snaps.json` | snapshots: reign era `era`, title `t`, description `d` | year |
| `misc.json` | sea names `sea`, modern province names `prov` | Chinese name |

`zh.lock.json` records a fingerprint (first 10 hex digits of the sha1) of the Chinese each English entry was written from. If the Chinese changes and the English does not, the build reports it as out of date. The naming rules (pinyin, foreign place names, lunar months, how battle outcomes are written, and so on) are in `content/en/GLOSSARY.md`.

**After changing Chinese text**:

1. `python tools/i18n.py status` shows how many entries are missing or out of date;
2. `python tools/i18n.py todo` lists their Chinese; add or revise the English in the matching JSON file;
3. `python tools/i18n.py lock` records the new Chinese fingerprints;
4. `python run.py --html` reassembles the page (strict mode stops on missing text).

`python tools/i18n.py table` exports every Chinese–English pair to `build/i18n-review.tsv` for review.

## 8. Tuning (`src/config.py`)

| Parameter | Default | Effect |
|---|---|---|
| `EXTENT` / `BASE_EXTENT` | 14°E–146°E, 10°N–62°N / 25°W–180°E, 11°S–82°N | territory extent / base-map extent (the latter affects only the base map) |
| `CELL` | 1.1 | grid cell size (projected units, about 7 km). Smaller is finer; time and memory grow roughly with the square |
| `RANGE_MAJOR` / `RANGE_MINOR` | (8.0, 26) / (3.5, 18) | peak cost and half-width (km) of main and minor ranges |
| `BORDER_RIVERS` | — | peak cost and half-width of border rivers |
| `NOISE_AMP` | 0.38 | amplitude of the smooth noise; larger makes boundaries wind more |
| `REACH` | 130 | cells beyond this cost distance (times each point's `R=` factor) are unclaimed |
| `SMOOTH_SIGMA` | 1.2 | smoothing of the partition (cells) |
| `WARP_AMP` | 1.6 | amplitude of the displacement field (cells), giving plains boundaries small bends |
| `SIMPLIFY_TERR` | 0.018 | coverage simplification tolerance (°); larger is coarser and smaller |
| `PRESET_HEX` / `PRESET_COLORS` | — | states with fixed colors |

## 9. Sources and reliability

- **Base map**: [Natural Earth](https://www.naturalearthdata.com/) 1:10m vector data (public domain), pinned at commit `ca96624`; ETOPO20 relief from the sample data of matplotlib basemap v1.4.1.
- **Modern provinces**: the simplified provincial borders of the Tang–Song transition map.
- **Historical sources**: for China, the Song, Liao, Jin and Yuan dynastic histories, the *Xu zizhi tongjian changbian* and the *Jianyan yilai xinian yaolu*, following in outline vols. 6–7 of Tan Qixiang's *Historical Atlas of China*; for Central Asia, West Asia and Europe, standard historical atlases and general national histories.
- **Limitations**:
  - Borders are indicative lines inferred from the allegiance of prefectures and towns, not researched historical boundaries.
  - On the steppe, the Tibetan plateau, in Siberia and Arabia the points are sparse and the borders especially rough; the "territory" of a nomadic state was never a line in the first place.
  - Changes between snapshots are not drawn; for events within one snapshot's period, the map shows only the state of affairs in the snapshot year.
  - Old river courses are drawn by hand following written sources and are approximate.
  - After 1260 the four khanates nominally acknowledged the Yuan Great Khan as overlord; the map treats them as the independent states they were in practice.
  - The English is translated from the Chinese; naming conventions are in `content/en/GLOSSARY.md`. Months in East Asia are lunar months and are not converted to the Western calendar.
