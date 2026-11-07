# 宋辽夏金元形势图 · Song, Liao, Xia, Jin and Yuan, 979–1279

中文 · [English](#english)

北宋统一至崖山（979—1279）的交互历史地图，中英双语：61 个时间节点的政权与路、道、兀鲁思、行省疆域，640 处州府城邑的古今地名对照，西至中欧、埃及，东至日本。另有 99 处都城行在、145 场战役、15 条行军路线、30 处关隘、58 项事件、70 条山脉、百余条河湖、燕云十六州与周边诸族。

上接《唐宋之际形势图》（755—979）：979 年节点的政权颜色与那张图最后一个节点一致。

---

## 一、直接看

双击 **`docs/index.html`**，用任意现代浏览器（Chrome、Edge、Safari、Firefox）打开即可。

这个文件约 4 MB，数据、样式、脚本全部内嵌：不联网、不需要服务器、不依赖任何外部库。可以直接拷到 U 盘、发给别人，或者放到自己的网站上。

- 时间轴：点刻度跳转，左侧 ▶ 播放，下方 1× / 2× 切换倍速；键盘 ← → 逐节点。
- 着色：顶栏「路·汗国 / 政权」切换。「路·汗国」模式下宋、金分路，辽分五京道，大蒙古国分兀鲁思，元分行省；1260 年后四大汗国各自成为政权。
- 斜线：藩属或附庸（如辽的阻卜、室韦、女真诸部，臣服于西辽的喀喇汗、花剌子模，臣服于蒙古的西夏、高丽、罗姆、小亚美尼亚、罗斯诸公国）。「政权」着色下它们并入宗主国的颜色，仍保留斜线、名称和细虚线轮廓。
- 视野：顶栏下拉框有全图、蒙古帝国与 16 个地区。
- 语言：地图右上角「中 | EN」切换（年表、对照表视图里在内容区右上角），选择会记在浏览器里；网址末尾加 `#en` 直接打开英文版。英文界面里地图只标英文，悬停说明、索引、年表、对照表在英文名后附注汉字原名；检索中英文都可以，英文不必打变音符号。

---

## 二、发布到 GitHub Pages

成品是纯静态单文件，不需要后端。

1. 把整个目录推到一个 GitHub 仓库（如 `songyuan-map`）。
2. 仓库 Settings → Pages：Source 选 **Deploy from a branch**，Branch 选 **main**，目录选 **/docs**，保存。
3. 一两分钟后即可在 `https://<用户名>.github.io/songyuan-map/` 访问。

以后每次改完运行 `python run.py`，把 `docs/index.html` 一起提交推送，网页就会自动更新。`docs/.nojekyll` 让 Pages 原样发布，不经 Jekyll 处理。

---

## 三、本地构建

改了史料内容（`content/`）或参数（`src/config.py`）之后才需要重新构建。需要 **Python 3.10 或更新版本**，内存 4 GB 以上。

**macOS / Linux**

```bash
cd songyuan-map
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py --open
```

**Windows（PowerShell）**

```powershell
cd songyuan-map
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py --open
```

完整构建约 15—20 分钟（栅格 200 余万格、61 个节点），完成后用浏览器打开新生成的 `docs/index.html`。

| 命令 | 作用 |
|---|---|
| `python run.py` | 底图缺失则下载 → 计算疆域 → 拼装 HTML |
| `python run.py --html` | 只重新拼装 HTML（只改了 `src/template.html` 时用，几秒钟） |
| `python run.py --open` | 构建完后在浏览器中打开 |
| `python run.py --html --draft` | 英文有缺译或过期时也照常生成（缺译处临时显示中文）；不加 `--draft` 时会报错停下 |
| `python tools/i18n.py status` | 英文版状态：缺译、过期、未登记指纹各多少条（详见第七节） |
| `python run.py --preview 1141,1279` | 额外画出这几个节点的疆域草图到 `build/preview-*.png` |
| `python tools/preview.py 1227 --box 100,112,34,42` | 只画草图，可指定经纬框（西,东,南,北）与 `--mode zhen` |
| `python tools/screenshot.py` | （可选，需 playwright）无头浏览器截图并检查脚本错误 |

压缩包里已经带了底图数据（`geodata/`，约 43 MB），离线也能构建；删掉后 `run.py` 会自动从 GitHub 下载固定版本（ETOPO 地形另做 sha256 校验）。

同一环境下，同一份输入的构建结果逐字节一致，可以放心用 git 追踪改动。

---

## 四、目录结构

```
songyuan-map/
├── run.py                 一键构建入口
├── requirements.txt
├── README.md
├── docs/
│   ├── index.html         ★ 成品，单文件（GitHub Pages 直接从 /docs 发布）
│   └── .nojekyll
├── content/               ★ 史料内容（手写，主要改这里）
│   ├── seeds.txt          787 个归属点（347 州府、293 城邑、147 区域辅助点）：古名、经纬度、今地、名称沿革
│   ├── snaps.txt          61 个时间节点：每个点在该年属哪个单位、哪个政权
│   ├── units.py           179 个政权、路、汗国、部族的名称与介绍
│   ├── items.py           都城、战役、关隘、事件、诸族
│   ├── items_geo.py       山脉、水系、湖泽、运河、荒漠、海名、燕云十六州、行军路线
│   └── en/                ★ 英文版：与上面各文件一一对应的译文（JSON）、zh.lock.json 中文指纹、GLOSSARY.md 译名体例
├── src/
│   ├── config.py          ★ 全部路径与可调参数（栅格、代价、平滑、配色……）
│   ├── fetch_data.py      底图缺失时下载固定版本
│   ├── build.py           计算疆域，输出 build/geo.json、build/data.json
│   ├── assemble.py        并入英文、检查缺译，把数据注入模板，输出 docs/index.html
│   ├── i18n.py            英文版：列出需要翻译的条目、检查缺译与过期、把译文并入数据
│   └── template.html      前端：页面结构、样式、交互脚本
├── geodata/
│   ├── prov.json          今中国省界（简化）
│   ├── ne/                Natural Earth 1:10m GeoJSON
│   └── etopo/             ETOPO20 全球地形
├── tools/
│   ├── i18n.py            英文版维护：status / todo / lock / table
│   ├── preview.py         matplotlib 疆域草图
│   └── screenshot.py      playwright 截图检查
└── build/                 中间产物（可随时删除）
```

---

## 五、工作原理

```
content/ ──────┐
               ├─► build.py ─► build/geo.json + data.json ─► assemble.py ─► docs/index.html
geodata/ ──────┘                                               ▲
                                                 src/template.html
```

### 1. 为什么疆域要“算”出来

史书能确定的是“某年某州属某国某路”，很少有连续的边界线。所以这里只手写**点 → 单位 → 政权**的归属（`snaps.txt`），再用一张“通行代价”地图让计算机推出点与点之间的分界，让分界尽量落在山脊和大河上。

### 2. `build.py` 的步骤

1. **读归属点**：`seeds.txt`。类型 `z` 是州府，`c` 是城邑或外域地名，`r` 是只用来占地、不在图上显示的区域辅助点。
2. **解析时间节点**：`snaps.txt` 是一个小型声明式语言（语法见下文）。每个 `@年份` 块继承上一节点的全部归属，只写变化的部分。
3. **投影平面栅格**：先投影（Albers 等积圆锥，标准纬线 25°N、47°N，原点 38°N、95°E），再在投影平面上切等距格子（边长约 7 km），西起 14°E、东至 146°E、南起 10°N、北至 62°N。面积 0.15 平方度以上的湖当作水面，咸海用历史湖岸，近代水库与近代形成的湖不画。
4. **代价栅格**：每格基础代价 1，加上：
   - ETOPO20 地形起伏与 2500 米以上的高原；
   - `items_geo.RANGES` 的山脉沿脊线“烧”出高斯形高代价带（主干峰值 +8，次要 +3.5），脊线先加横向摆动；
   - Natural Earth 山地多边形整体加一点代价；
   - 界河（长江、淮河、汉水、阿姆河、锡尔河、多瑙河、伏尔加河、幼发拉底河……以及手绘的淮河古下游、宋辽界河白沟河）；
   - 最后乘 ±38% 的多尺度平滑噪声，让平原上的界线也有自然的曲折。
5. **多源最短路**：所有归属点作为源，在 16 邻接（含马步）陆地网格上跑一次 `scipy.sparse.csgraph.dijkstra(min_only=True)`，每格归代价距离最近的点。超出可达代价的格子为无主地；外缘做闭运算、填小洞、高斯平滑，再叠一层平滑位移场。
6. **出多边形**：逐节点按归属分区，在相邻两类平滑值相等处描出共享界线（三类以上交汇取交点均值），全图界线只描一次、两侧共用，做三轮拉普拉斯平滑；再用 shapely `polygonize` 拼成覆盖图，`coverage_simplify` 整体简化。政权界、单位界都由同一批共享边合成，不会留缝或叠色。相邻节点没变的几何只存一份（`GEO.pool`）。
7. **配色**：与唐宋图衔接的政权直接沿用那张图的颜色（`PRESET_HEX`）；金、蒙古、西辽、花剌子模、塞尔柱、拜占庭与四大汗国给定色相（`PRESET_COLORS`）；其余在 OKLCH 低彩度色板里按全部节点的邻接关系贪心着色。深色主题统一提亮。
8. **底图与条目**：海岸、今国界、湖泊、荒漠来自 Natural Earth。底图画到比疆域大得多的 `BASE_EXTENT`（西经 25° 至东经 180°、南纬 11° 至北纬 82°），疆域范围外的陆地罩一层薄纸色并以虚线标出疆域范围；河流按 `NE_RIVERS` 映射成古名（Huang → 河、Amu Darya → 阿母河、Volga → 亦的勒河……）。黄河下游按年代画三条河道：京东故道（至 1048）、北流（1048—1128）、南流夺淮（1128 年后），郑州以东的今黄河画成虚线。

### 3. 前端（`src/template.html`）

- **零依赖**：原生 JavaScript + SVG。
- **图层（自下而上）**：陆地 → 荒漠点纹 → 疆域填色 → 藩属斜线 → 政权粗边界 → 燕云十六州 → 湖泊 → 今省界 → 今国界 → 山脉 → 河流 → 运河 → 疆域范围外的薄罩与范围线 → 行军路线、点符号与注记。
- **时间**：每个节点涵盖“上一节点之后至本节点”的年份。战役、事件、行军路线只显示本期的；行军路线本期走过的一段画实线加箭头，此前走过的画虚线。在索引、年表里点其他时期的条目，时间轴自动跳过去。
- **都城**：只显示当期都城（实心框）和已经做过都城的旧都（虚线框）。
- **主题**：颜色全部是 CSS 变量，跟随系统深浅色；每个单位的颜色是 `--u-<序号>`，由 `assemble.py` 注入。
- **语言**：全部文字按当前语言取值（`LZ(中, 英)` 与 `iF(条目, 字段)` 等几个取值函数），切换时重绘地图、索引、年表与对照表。英文注记用画布实测宽度参与避让，疆域里放不下的长名自动折成两行。

### 4. `assemble.py`

模板里有 4 个占位符：`__GEO__`、`__DATA__`、`__UCSS_LIGHT__`、`__UCSS_DARK__`。脚本先用 `src/i18n.py` 检查英文是否齐全、是否过期（不齐全就报错停下，`--draft` 除外），再把英文并入数据（单位 `ne`/`se`/`notee`，州府 `ne`/`nme`/`mode`，条目 `e`，节点 `erae`/`te`/`de`/`labe`），最后替换占位符，包上 `<!doctype html>` 等文档外壳。

---

## 六、常见修改

**改某地某年的归属**：在 `snaps.txt` 对应年份块里加一行，例如 1141 年把海州划给金：

```
山东东路: 海州
```

**新增一个点**：在 `seeds.txt` 加一行 `ID 经度 纬度 今地 [类型] [N=年:名,…]`，再在 `snaps.txt` 第一个节点（或它出现的节点）分给某个单位，运行 `python run.py --preview 年份` 检查。

**地名改名**：在 `seeds.txt` 该行加 `N=0:旧名,年份:新名`，如 `N=0:杭州,1129:临安府`。

**新增时间节点**：在 `snaps.txt` 两个节点之间插入 `@年份 | 年号 | 标题 | 说明`，写出这一年相对上一节点的变化。前端会自动多出一个刻度。

**加战役、关隘、事件、都城**：在 `items.py` 照格式加一条元组。战役和事件会按年份自动归入对应节点；持续多年的事件在 `EVENT_END` 写上结束年份。

**加行军路线**：在 `items_geo.ROUTES` 加一条，`pts` 每点写 `[经度, 纬度, 到达年, 地名]`。

**加政权、路、部族**：在 `units.py` 用 `S(...)`（政权）、`Z(...)`（下属单位）、`T(...)`（部族）加一条，再在 `snaps.txt` 里使用它的键。

**边界不该翻过某座山**：在 `items_geo.RANGES` 里加这条山的脊线坐标，最后一位设为 `1`（主干，代价更高）。

**只改页面样式或交互**：编辑 `src/template.html`，然后 `python run.py --html`。

**新增或改动了任何中文**（点、条目、单位、节点说明……）：同时补写或改写 `content/en/` 里的英文，否则严格构建会报缺译或过期，见第七节。

### `snaps.txt` 语法速查

```
@年份 | 年号 | 标题 | 说明                      开始一个时间节点（继承上一节点）
单位: 点 点 点                                  把这些点划给单位
单位[显示名]{治所}>所属政权: 点 ……              同时设定本期显示名、治所、隶属（都可省略）
单位[]:                                         清除显示名，恢复 units.py 里的名字
单位: @另一单位                                  把“本节点开始时”属于另一单位的点全部划过来
单位: @另一单位@年份                             把“某年节点结束时”属于另一单位的点划过来
·: 点 点                                        设为无主
藩属: 单位 单位 ……                               本期的藩属、附庸（地图加斜线），整行替换上期
+藩属: 单位 / -藩属: 单位                         在上期名单上增减
# 注释
```

“所属政权”缺省时取 `units.py` 的默认值。显示名、治所、隶属一经设定会延续到后面的节点，直到再次改写。

---

## 七、英文版

中文是源文本，英文按同样的键写在 `content/en/` 里：

| 文件 | 内容 | 键 |
|---|---|---|
| `units.json` | 政权、路、汗国、部族：全称 `n`、地图短名 `s`、说明 `note` | 单位键（如 `宋`） |
| `labels.json` | 节点里的当年别名（`snaps.txt` 的 `[显示名]`） | 中文别名 |
| `seeds.json` | 州府城邑：今地 `mod`、各时期名称 `n` | 点的 ID |
| `items.json` | 条目：`old` `mod` `note` `yt` `sides` `cmd` `tag`，地域分区 `g`，路线地名 `p` | `类别:古名`（如 `battle:高梁河之战`） |
| `snaps.json` | 时间节点：年号 `era`、标题 `t`、说明 `d` | 年份 |
| `misc.json` | 海名 `sea`、今省名 `prov` | 中文名 |

`zh.lock.json` 记着每条英文写成时对应中文的指纹（sha1 前 10 位）。中文改了而英文没改，构建就报“过期”。译名与写法的规矩见 `content/en/GLOSSARY.md`（拼音、外国地名、农历月份、战役胜负的写法等）。

**改了中文之后**：

1. `python tools/i18n.py status` 看有几条缺译、过期；
2. `python tools/i18n.py todo` 列出这些条目的中文，到对应 JSON 里补写或改写英文；
3. `python tools/i18n.py lock` 记下新的中文指纹；
4. `python run.py --html` 重新拼装（严格模式，缺译会报错）。

`python tools/i18n.py table` 导出全部中英对照到 `build/i18n-review.tsv`，便于审校。

---

## 八、调参（`src/config.py`）

| 参数 | 默认 | 作用 |
|---|---|---|
| `EXTENT` / `BASE_EXTENT` | 14°E—146°E、10°N—62°N / 25°W—180°E、11°S—82°N | 疆域计算范围 / 底图范围（只影响底图，不影响疆域） |
| `CELL` | 1.1 | 栅格边长（投影单位，约 7 km）。调小更精细，时间与内存约按平方增长 |
| `RANGE_MAJOR` / `RANGE_MINOR` | (8.0, 26) / (3.5, 18) | 主干、次要山脉的代价峰值与半宽（km） |
| `BORDER_RIVERS` | — | 界河的代价峰值与半宽 |
| `NOISE_AMP` | 0.38 | 平滑噪声幅度，越大界线越曲折 |
| `REACH` | 130 | 超出此代价距离（再乘各点 `R=` 倍数）的格子算无主地 |
| `SMOOTH_SIGMA` | 1.2 | 分区平滑程度（格） |
| `WARP_AMP` | 1.6 | 位移场幅度（格），让平原界线带小弯 |
| `SIMPLIFY_TERR` | 0.018 | 覆盖简化容差（°），越大越粗略、文件越小 |
| `PRESET_HEX` / `PRESET_COLORS` | — | 固定色的政权 |

---

## 九、资料与可靠程度

- **底图**：[Natural Earth](https://www.naturalearthdata.com/) 1:10m 矢量数据（公有领域），固定在提交 `ca96624`；ETOPO20 地形取自 matplotlib basemap v1.4.1 示例数据。
- **今省界**：沿用《唐宋之际形势图》的简化省界。
- **史料**：中国部分据《宋史》《辽史》《金史》《元史》《续资治通鉴长编》《建炎以来系年要录》，参照谭其骧《中国历史地图集》第六、七册大意；中亚、西亚、欧洲部分据通行史地图集与各国通史大意。
- **局限**：
  - 疆域边界是由州府城邑的归属推算的示意线，不是考证出的历史界线。
  - 草原、青藏、西伯利亚、阿拉伯半岛等地归属点稀疏，边界尤其粗略；游牧政权的“疆域”本来就不是线。
  - 节点之间的变化没有画出来；同一节点内先后发生的事，图上只取节点年份的结果。
  - 古河道按文献走向手绘，是近似线。
  - 1260 年后四大汗国名义上仍奉元朝大汗为共主，图上按实际各自为政处理。
  - 英文据中文翻译，名称体例见 `content/en/GLOSSARY.md`；东亚的月份是农历月序，不换算公历。

---
---

## English

[中文](#宋辽夏金元形势图--song-liao-xia-jin-and-yuan-9791279) · English

An interactive historical map of East Asia and Eurasia from the Song reunification to the fall of the Song at Yamen (979–1279), in Chinese and English: the territories of states, circuits, uluses and provinces at 61 snapshots, with historical and modern names for 640 prefectures and towns, from central Europe and Egypt in the west to Japan in the east. It also shows 99 capitals, 145 battles, 15 campaign routes, 30 passes, 58 events, 70 mountain ranges, more than a hundred rivers and lakes, the Sixteen Prefectures of Yan and Yun, and the peoples on the periphery.

It continues the *Tang–Song transition* map (755–979): the colors of the states at the 979 snapshot match the last snapshot of that map.

### 1. Just look

Double-click **`docs/index.html`** and open it in any modern browser (Chrome, Edge, Safari, Firefox).

The file is about 4 MB with all data, styles and scripts embedded: no network, no server and no external libraries. You can copy it to a USB stick, send it to someone, or put it on your own website.

- Timeline: click a tick to jump; ▶ on the left plays, 1× / 2× below it changes speed; the ← → keys step through snapshots.
- Coloring: the "Circuits & uluses / States" switch in the top bar. In "Circuits & uluses" mode Song and Jin are divided into circuits, Liao into its five capital circuits, the Mongol Empire into uluses and the Yuan into provinces; after 1260 the four khanates are states of their own.
- Hatching: vassals and tributaries (for example the Zubu, Shiwei and Jurchen tribes under Liao; the Kara-Khanids and Khwarazm under the Western Liao; Western Xia, Goryeo, Rum, Cilician Armenia and the Rus' principalities under the Mongols). In "States" mode they take their overlord's color but keep their hatching, name and thin dashed outline.
- View: the drop-down in the top bar offers the whole map, the Mongol Empire and 16 regions.
- Language: the "中 | EN" switch at the top right of the map (at the top right of the content in the Timeline and Gazetteer views); the choice is remembered by the browser, and adding `#en` to the URL opens the English version directly. In English the map labels are in English only, while tooltips, the index, the timeline and the gazetteer add the original Chinese characters after each English name. Search works in both languages, and English searches ignore diacritics.

### 2. Publish on GitHub Pages

The result is a single static file and needs no back end.

1. Push the whole directory to a GitHub repository (e.g. `songyuan-map`).
2. In the repository's Settings → Pages, set Source to **Deploy from a branch**, Branch to **main** and the folder to **/docs**, and save.
3. After a minute or two the map is live at `https://<username>.github.io/songyuan-map/`.

After each change, run `python run.py` and commit and push `docs/index.html` with it; the site updates automatically. `docs/.nojekyll` makes Pages publish the files as they are, without Jekyll.

### 3. Build locally

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

### 4. Directory layout

```
songyuan-map/
├── run.py                 one-step build entry point
├── requirements.txt
├── README.md
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

### 5. How it works

```
content/ ──────┐
               ├─► build.py ─► build/geo.json + data.json ─► assemble.py ─► docs/index.html
geodata/ ──────┘                                               ▲
                                                 src/template.html
```

#### Why the territories are computed

What the histories can tell us is that "in a given year a given prefecture belonged to a given state and circuit"; they seldom give continuous boundary lines. So only the allegiance **point → unit → state** is written by hand (`snaps.txt`), and a "travel cost" map lets the computer work out the boundaries between points, making them follow ridges and great rivers wherever possible.

#### What `build.py` does

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

#### The front end (`src/template.html`)

- **No dependencies**: plain JavaScript and SVG.
- **Layers (bottom to top)**: land → desert stipple → territory fill → vassal hatching → heavy state borders → the Sixteen Prefectures → lakes → modern provinces → modern borders → mountains → rivers → canals → veil and dashed line outside the territory extent → campaign routes, symbols and labels.
- **Time**: each snapshot covers the years after the previous snapshot up to its own year. Battles, events and campaign routes are shown only for the current period; the stretch of a route covered in this period is drawn solid with arrows, earlier stretches dashed. Clicking an item from another period in the index or timeline moves the timeline there.
- **Capitals**: only current capitals (solid squares) and former capitals (dashed squares) are shown.
- **Themes**: all colors are CSS variables and follow the system's light or dark theme; each unit's color is `--u-<index>`, injected by `assemble.py`.
- **Language**: every piece of text is taken in the current language through a few accessor functions (`LZ(zh, en)`, `iF(item, field)` and others), and switching redraws the map, index, timeline and gazetteer. English labels are measured on a canvas for collision avoidance, and long names that do not fit inside a territory wrap onto two lines.

#### `assemble.py`

The template has four placeholders: `__GEO__`, `__DATA__`, `__UCSS_LIGHT__` and `__UCSS_DARK__`. The script first uses `src/i18n.py` to check that the English is complete and up to date (stopping with an error if not, unless `--draft` is given), then merges the English into the data (units `ne`/`se`/`notee`, points `ne`/`nme`/`mode`, items `e`, snapshots `erae`/`te`/`de`/`labe`), replaces the placeholders, and wraps the result in the `<!doctype html>` document shell.

### 6. Common changes

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

#### `snaps.txt` syntax

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

### 7. The English version

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

### 8. Tuning (`src/config.py`)

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

### 9. Sources and reliability

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
