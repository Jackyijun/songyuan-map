# 英文版译名与体例（GLOSSARY）

中文是源文本，英文按同一套键写在本目录的 `*.json` 里（结构见 `src/i18n.py` 开头）。本文件记录译名体例，新增或修改英文时照此执行；同一个名称在全图各处必须写法一致（地图注记、悬停说明、索引、对照表、年表、节点说明）。

## 一、总原则

1. **说真话**：英文只翻译中文已有的内容，不增不减；中文本身有误时先改中文，再改英文（并运行 `python tools/i18n.py lock`）。
2. **通俗写法，全图统一**：采用英文读者最常见的写法（Genghis Khan、Kublai、Hulagu、Kyiv、Bukhara），不用学术转写（Činggis Qa'an、Qubilai）。
3. **地名用当时当地的名称**：中国及汉字文化圈的地名用汉语拼音转写中文古名；汉字圈以外的地名用当地当时名称的通行英文写法，而不是把中文译音再转回拼音（八剌沙衮 → Balasagun，不写 Balashagun；亦的勒河 → Itil）。
4. **今地/今名**用今天的通行英文名和行政区（Kaifeng, Henan；Şanlıurfa, Turkey）。行政区划变了中英文一起改（越南 2025 年 7 月并省：广南并入岘港、平定并入嘉莱、广平并入广治、永福并入富寿）。
5. **地图注记不加中文里没有的消歧义**：同音的不同地名（郁水、淯水都作 Yu River）照写，靠位置和悬停里的汉字区分；中文自带的区别字样照译（洛水（北）→ Northern Luo River）。“今地 / 今名”一栏是给英文读者定位用的，英文同名时可括注地区（Min River (Fujian)），英文读者更熟悉另一通行名时可括注（Nu River (Salween)）。
6. **政权全称可括注英文通行的别称**（Western Liao (Qara Khitai)、Gusiluo (Tsongkha)），地图短名不括注。
7. 英文界面里，地图注记只显示英文；悬停说明、索引、对照表、年表在英文名后附注汉字原名。
8. **按语末的“（今名）”**表示条目名称是今名、当时没有这个名称；英文一律放在按语最末，写作 “The name is modern.”，不夹在句中（夹在句中容易被读成前一个名词是今名）。

### 常用词

| 中文 | 英文 | 说明 |
|---|---|---|
| 岁贡 / 岁币 | annual tribute / annual payments | 1165 年隆兴和议把宋对金的“岁贡”改称“岁币”，两词不混用；海上之盟、赎燕的“岁币”也作 annual payments |
| 留守 | custodian (of X) | 东京留守 custodian of the Eastern Capital；不用 regent（摄政另有其义） |
| 节度使 | military governor | 宋太祖任归德军节度使 military governor of Guide Jun |
| 西域南道 / 北道 | Southern / Northern Route of the Western Regions | 全图统一，不写 southern Silk Road |
| 义父 | adoptive father | 不用 sworn father（那是安答、结义） |
| 中流 | midstream | 绍兴和议“以淮水中流为界” the midstream of the Huai |

## 二、拼音与通名

| 类别 | 写法 | 例 |
|---|---|---|
| 拼音 | 不标声调；音节界限有歧义时加撇号；ü 保留 | Xi'an、Lin'an、Yelü、Lüliang |
| 州（单音节专名） | 连写 | 汴州 Bianzhou、灵州 Lingzhou |
| 州（多音节专名） | 分写 Zhou | 东胜州 Dongsheng Zhou |
| 府 / 军 / 监 | 分写，不意译；作路名的一部分时同样分写 | 开封府 Kaifeng Fu、镇戎军 Zhenrong Jun、仙井监 Xianjing Jian、永兴军路 Yongxing Jun Circuit |
| 城（城名的一部分） | City；英文已有定名的从定名 | 青唐城 Qingtang City、可敦城 Kedun City、钓鱼城 Diaoyu Fortress |
| 京（陪都） | 府名在前，京名意译加括注 | 临潢府（上京）Linhuang Fu (Supreme Capital)；Daxing Fu (Zhongdu) |
| 关 / 口 / 岭（关隘类） | Pass；已成专名者照拼 | 潼关 Tong Pass、大庾岭 Dayu Pass、古北口 Gubeikou、野狐岭 Yehuling |
| 水 / 河 / 江（单音节专名） | X River；与他河撞名或英文惯用 -shui 的连写 | 汾水 Fen River、淮水 Huai River；湟水 Huangshui、弱水 Ruoshui、黑水 Heishui（与今黑河 Hei River 区别） |
| 海名 / 湖名 | Lake X 或 X Lake，从英文习惯 | 太湖 Lake Tai、洞庭湖 Dongting Lake |
| 山 | 山脉 X Mountains；单峰 Mount X；英文惯称照用 | 太行山 Taihang Mountains、泰山 Mount Tai、横山 Hengshan Range（与恒山 Heng Mountains 区别） |
| 羁縻 | loose-rein | 羁縻州 loose-rein prefectures |
| 蛮 / 蛮地 | tribes / tribal land（不用 barbarian） | 两林蛮 Lianglin tribes |
| 行在 / 行朝 | temporary capital / court in flight | 临安府（行在）Lin'an Fu (temporary capital) |

## 三、政区层级

| 中文 | 英文 | 说明 |
|---|---|---|
| 宋 路 | Circuit，路名拼音、方位意译 | 京东东路 Jingdong East Circuit |
| 辽 道 | Circuit，京名意译 | 上京道 Supreme Capital Circuit |
| 金 路 | Circuit，路名拼音 | 上京路 Shangjing Circuit、北京路 Beijing Circuit |
| 蒙古 兀鲁思 | Ulus of X | 术赤兀鲁思 Ulus of Jochi |
| 元 行省 | X Province | 岭北 Lingbei Province |
| 府界 | Capital District | 开封府界 Kaifeng Capital District |
| 伪齐 | Qi (Jin client state) | 地图短名 Qi |

## 四、人名、政权、王朝

- 汉人名：姓在前、拼音（Yue Fei、Han Shizhong）；帝王用“Emperor + 庙号 + of + 朝”（Emperor Taizong of Song）或通行称呼（Emperor Tianzuo）。
- 契丹、女真、党项人名按汉文史籍拼音（Yelü Dashi、Wanyan Aguda、Li Yuanhao）；兀术写作 Wuzhu（Wanyan Zongbi）。
- 蒙古人名用通行英文写法：Genghis Khan、Temüjin、Kublai、Hulagu、Möngke、Ögedei、Batu、Subutai、Jebe、Tolui、Ariq Böke、Kaidu。
- 朝鲜用新罗马字（Goryeo、Gaegyeong、Gang Gam-chan）；日本用平文式（Heian-kyō、Minamoto no Yoshitsune）；越南保留声调符号（Đại Việt、Lý Thường Kiệt、Thăng Long）。
- 罗斯与乌克兰地名用今乌克兰拼法（Kyiv、Chernihiv、Halych、Volodymyr），国家称 Kievan Rus'。罗斯人名用英文通行写法并全图统一：Volodymyr the Great、Yaroslav the Wise、Mstislav（父名 Mstislavich）、Yuri；“大公”译 Grand Prince。
- 伊斯兰世界人名去掉长音符号的通行写法（Alp Arslan、Jalal al-Din、Nur ad-Din、Saladin、Baybars）；喀喇汗统一作 Kara-Khanid(s)。
- 种姓读 Chóng（种师道 Chong Shidao）；女真复姓按拼音连写（独吉思忠 Duji Sizhong）；完颜陈和尚的“陈和尚”是名，连写 Wanyan Chenheshang。
- 生于高丽或朝鲜半岛出身的元将用新罗马字（洪茶丘 Hong Da-gu）。
- 和议、盟约一律作 Treaty of X（Treaty of Chanyuan、Treaty of Qingli、Treaty of Shaoxing、Treaty of Longxing）。
- 政权名见 `units.json`：地图上用短名（s），说明里用全称（n）。

## 五、年代

- **东亚（宋、辽、夏、金、元、高丽、日本、越南）**：中文写农历月份，英文照写农历月序，不换算公历：
  - 979 年五月 → 5th month, 979；闰九月 → intercalary 9th month；正月 → 1st month
  - 春、夏、秋、冬 → spring / summer / autumn / winter 981
  - 年份是该农历年大部分所在的公历年，所以十二月可能已在次年 1 月；必要时括注公历（12th month, 1141 (January 1142)）。
- **其他地区**：中文写的月份即儒略历月份，英文用月名：August 1071、9 April 1241。
- 年号：Taiping Xingguo 4（年号拼音 + 序数，不写 “4th year of”）。
- 约 → c.；年份区间用 en dash：1069–1085。

## 六、战役

- 名称：Battle of X / Siege of X / Fall of X / Sack of X，英文已有通行名称的用通行名称（Battle of Manzikert、Battle on the Ice、Battle of Yamen）。
- 同地多次战役，中文以年号、别名或年份区别的（灵州之战、元丰灵州之战、灵州之战（黄河九渡）），英文统一以年份括注区别：Battle of Lingzhou (1002) / (1081) / (1226)。这是第一节第 5 条的唯一例外。
- 交战结果：“A defeated B”，城破加注 “(city fell)”，关寨、小城分别作 “(fort fell)”、“(town fell)”；中文另有说明时照译括注（Jin withdrew north after a negotiated settlement）。
- 主将：“A and B vs. C”。

## 七、维护

- `python tools/i18n.py status`：缺译、过期、未登记指纹的条数。
- `python tools/i18n.py todo [文件]`：逐条列出缺译与过期的中文。
- 改完英文：`python tools/i18n.py lock` 记下中文指纹；以后中文一改，对应英文就会报“过期”。
- `python run.py --html` 默认严格：有缺译或过期就停下；`--draft` 允许先出草稿（缺译处显示中文）。
- `python tools/i18n.py table` 导出中英对照表 `build/i18n-review.tsv` 供审校。
