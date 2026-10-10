# WWMI MOD 面板助手 (WWMI MOD Panel Helper)

> 读取鸣潮 (Wuthering Waves) MOD 的按键配置，一键生成游戏内快捷切换面板。
> Read a WuWa mod's key config and inject a quick-toggle panel into the game in one click.

---

## 制作目的 / Purpose

鸣潮很多 MOD 用键盘组合键切换服装、头发、眼睛等部件（如 `右Shift+8`、`CTRL 1`、`ALT UP`）。
玩家要记住一大堆按键，非常麻烦。

本工具读取 MOD 配置里的按键切换段（`[KeyXXX]`），自动为 MOD **生成一个游戏内透明面板**：
按 `\`（默认，可在设置里改）呼出面板，点按钮即可触发对应切换，不用再记按键。

> 关键设计：面板**直接注入 MOD 自身的 ini**（不是额外附加文件），因为 3DMigoto 的
> CommandList 赋值只在"所在文件"的作用域内生效——附加文件里的赋值，MOD 原 override 读不到，
> 按钮会"有反馈但功能不变"。注入自身 ini 才能让按钮赋值真正命中原 `global persist` 变量。

---

## 功能 / Features

- **一键添加面板**：选择 MOD 文件夹 → 选标注方案 → 自动注入面板
- **透明面板**：背景几乎隐形，按钮/白色细边与背景有明显差异，不遮挡角色
- **两种按钮标注方案**：
  - **方案1（含义）**：自动读取按键段后缀翻译成中文（`KeyToufa → 头发`、`Keyshoes → 鞋`）
  - **方案2（编号）**：按钮统一标注 1、2、3…，适合后缀无意义的 MOD
  - 方案1 失败会自动回滚并询问是否改用方案2
- **智能按钮识别**：**一个按键段 = 一个按钮**（多取值是同一个按钮轮播，不会建多个按钮）；
  自动排除 UI/鼠标辅助段、备份文件；跨文件按变量去重（多形态 MOD 不重复计数）
- **角色检测**：面板只在**对应角色**在场时才能呼出（见「角色检测机制」）
- **面板可拖动**：按住顶部空白条拖动，自动钳制在屏幕内；右上角关闭按钮
- **开关按钮变暗**：二值开关按钮 off 时变暗，多值切换按钮恒定显示
- **默认调出键 `\`**（可设置/自动避开 MOD 已用键）
- **备份与回滚**：每次注入自动备份（`mod.ini.<时间戳>.bak_panel`）
  - 备份列表：**双击回滚**、**右键菜单**（单独回滚 / 增大 / 缩小 / 加长 / 加宽 / 重置按钮）、
  - 顶部：**一键回滚全部**、**清除记录**（只清列表不删 .bak）
- **修改按钮文字**：可编辑按钮文字并重新生成（配置文件 `zz_panel_labels.json`）
- **翻译词典**：内置大量英文/拼音部件词条——支持**大写开头**（`Toufa→头发`）、
  **swap/switch/toggle 前缀**（`SwapXiongbu→互换胸部`）、**组合词拆分**（`HairLong→头发长`）、
  数字后缀（`Yanjing2→眼睛2`）；英文界面下按钮**不翻译**（显示原词），
  未收录的可直接改 `zz_panel_labels.json`
- **面板键列**：记录列表显示每个 MOD 的**面板调出键**（注入时自动避开已占用键，各 MOD 可能不同，
  忘了就来看这列）；备份列表底部还有 **一键扫描**：从 Mod 起始文件夹扫出所有已注入面板的 MOD 并恢复记录
  （误清记录后也能找回，恢复回滚能力）
- **目录输入框**：顶部选中目录直接显示在输入框里（选完即可看到路径，不用猜）
- **中英双语**：首次打开选语言 + 选 Mod 起始目录，设置中可随时改
- **AI 修复提示词**：内置完整方法论（3DMigoto 规则 + 已验证结构 + 失败案例 + 排查步骤），
  一键复制发给任意 AI 可继续排查/完善（独立文件 `AI_PROMPT.md`）

---

## 使用方法 / Usage

1. 打开工具（`WWMI_MOD面板助手.exe`，或 `python src/main.py`）
2. 点「选择 Mod 文件夹」，选中 MOD 目录（含 `.ini` 与 `Textures/` 的文件夹）
3. 点「一键添加面板」→ 选标注方案
4. 多 ini 的 MOD 会弹窗让你选注入哪个文件（`>>` 为推荐项；面板调不出就换一个再试）
5. 成功后在游戏里按 **F10** 热重载（**无需退出游戏**）
6. 按 **`\`** 呼出面板；点按钮即触发切换；顶部空白可拖动、右上角 X 关闭
7. 备份记录列表里可回滚 / 右键微调按钮大小 / 双击打开配置文件
8. 误清了记录？点「一键扫描」从 Mod 起始文件夹扫回所有已注入面板的 MOD（含面板键与备份）

> 提示：角色不在场时面板调不出属正常（角色检测）；若按钮有反馈但切换无效，
> 多半是注入文件与 override 不在同一个 ini（见「工作原理」）。

---

## 工作原理 / How It Works

### 3DMigoto 变量作用域（核心，务必理解）

| 变量写法 | 作用域 |
|---|---|
| `global $x` | 所有命名空间 / CommandList 可见 |
| `global persist $x` | 同上，且保存到 d3dx_user.ini（按键切换常用） |
| `$\ns\x` | 仅该命名空间 |
| `$x`（无前缀） | **仅当前 CommandList 所在文件**（Local） |

- **Key 段**（原按键）在按键事件的全局上下文执行，无前缀赋值命中全局变量 → **跨文件有效**。
- **CommandList**（面板按钮走的通道）里无前缀赋值只落在**该 CommandList 所在 ini** → **不跨文件**。
- 因此：面板按钮要改的变量属于哪个 override，面板就必须注入**那个 ini**（同文件）。
  这就是本工具"注入式"（写进 MOD 自身 ini）而不是"附加文件"的原因。

### 面板结构（样式1，唯一验收方案）

```
[Constants]             # 面板全部状态与几何参数（$zz_open/$zz_fx/$zz_bw…）
[KeyToggleZZUI]         # 呼出：condition=<检测> key=\ type=cycle $zz_open=0,1
[KeyMouseZZ]            # 捕获左键：condition=$zz_open key=VK_LBUTTON type=hold $zz_holded=1 $zz_clicked=1
[Present]               # 每帧：if $zz_open { run Init; run Draw; $zz_clicked=0 }（+ post 归零检测变量）
[CommandListZZInit]     # 读窗口/渲染目标分辨率与鼠标坐标
[CommandListZZDraw]     # 画背景/标题/关闭钮/每个按钮（ps-t100 切 on/off 图）
[CommandListZZBtnN]     # 按钮 N：鼠标在区域内 && $zz_clicked → run ToggleN
[CommandListZZToggleN]  # 按钮变量轮播（一 Key 段 = 一按钮，多值轮播）
[CommandListZZDrag]     # 增量拖动 + 边界 clamp（验收版，勿改）
```

资源：`zz_panel_res\btn_N.png`（on）/`btn_N_off.png`；标签 `zz_panel_labels.json`。

### 角色检测（面板只在对应角色可调出）

- **reuse**：MOD 已有检测变量（`$active` / `$object_detected` 等，在 Key 段 condition 里使用且有置位）
  → 面板 Key condition 直接用它。⚠ 该变量必须与面板**同一文件**置位/读取。
- **self**：MOD 没有检测变量 → 自建 `[TextureOverrideZZDetect]`（复用人物网格 hash +
  `match_first_index`）→ 命中置 `$zz_detected=1`，Present post 归零。⚠ 检测段必须与
  KeyToggleZZUI **同一文件**，且放在"同 hash 竞争少"的 ini（否则匹配不到 draw，变量恒 0）。
- **none**：无条件（任何角色可呼出，仅测试用）。

---

## 多 ini / 多形态 MOD（重要，含踩坑记录）

- 多形态 = 多个 ini（如 `lupa playable` / `lupa cutscene` / `tail_controller`），
  同名变量各自独立（无前缀 = 文件级）。
- 面板必须注入 **override 所在文件**；检测链（Key + 检测 + Present）也必须同文件。

### 已知失败案例：露帕 (Lupa) 多形态

露帕是 cutscene / playable / tail 三文件 + `tail_controller`（`namespace=lupa\Master`）混用：

| 尝试 | 结果 |
|---|---|
| 注入 cutscene + self 检测 | 面板能呼出，但只有 Swap（显式 `$\lupa\Master\swapvar` 跨 ns）有效，其余按钮赋值落在 cutscene、playable 读不到 |
| 注入 playable + self 检测 | 面板连**无条件 Key** 都呼不出（playable 内 40+ 段共用同一网格 hash，检测段竞争不到 draw） |
| 检测段拆到 cutscene / condition 用 `$object_detected` | 均呼不出（跨文件赋值/读取失效） |

**结论**：露帕类（多形态 + namespace 混用）MOD 的面板支持暂不可行，工具会照常尝试，
失败原因见 `AI_PROMPT.md`——留给下一个 AI 用 F8 转储 + log 排查，或明确标注"不支持"。
其余已确认可用：守岸人（self 检测）、尤诺（reuse）、绯雪/达妮娅（作者原生面板，段名不撞即常态可用）。

---

## 踩坑记录（给开发者 / 下一个维护者）

1. **附加文件注入无效**：早期 `zz_panel.ini` 独立注入，按钮赋值跨文件失效
   → 改为**注入 MOD 自身 ini**（CommandList 赋值同文件命中）。
2. **54 按钮 bug**：曾把一个"0/1/3 轮播"的按键建成 3 个按钮 → 规则定为**一个 Key 段 = 一个按钮**。
3. **按钮错位/跑出面板**：背景 alpha 过低产生透明视觉错觉 → alpha 提到 110/120。
4. **调出键曾变成 y**：候选列表第一个字母被误选 → 默认固定 `\`，仅当被 MOD 占用才换。
5. **样式2（多页分页）全部失败**：重叠/错位/只有第 1 页可用，v2–v13 尝试后**弃用**，只保留样式1。
6. **拖动丢失**：曾因改动 Present 归零逻辑导致面板无法拖动 → 恢复验收版拖动结构
   （单 `[KeyMouseZZ]` hold 置位 + Present 不归零 holded + 增量 clamp），**此结构禁止再改**。
7. **跨文件检测失效**：`$zz_detected` 无前缀赋值是文件级，检测段与 Key 段不在同一文件就恒 0
   → 检测链必须同文件。
8. **多 ini 注入选错文件**：按键分布在多个 ini → 弹窗让用户选注入文件（`>>` 推荐），
   面板调不出就换文件重试（露帕 playable/cutscene 即为典型）。
9. **翻译识别不足**：作者常用拼音且大小写混杂（`Toufa`）、组合词（`HairLong`）
   → 词典扩充 + `lower()` 归一 + 组合词拆分。

---

## 自定义 / Customization

- **按钮文字**：记录列表「修改按钮文字」，或改 `zz_panel_labels.json` 后重开面板
- **调出键**：设置里改「面板调出键」（默认 `\`，A-Z/0-9 最稳）
- **按钮大小**：记录列表右键 → 增大/缩小/加长/加宽/重置
- **Mod 起始文件夹**：设置里改，选择 Mod 时从该目录开始浏览
- **词典**：本工具词典在 `src/engine.py` 的 `LABEL_MAP`（欢迎 PR 扩充）；用户可用 `user_dict.json` 自行扩展（见下）

### 自定义图片面板（测试功能，v2.3+）
- 设置 → 勾选 **「图片自定义（测试功能）」**；此后一键添加面板会先弹注入方式选择：
  - **通用注入**：默认文字按钮（和平常一样）
  - **自定义注入**：第一栏显示**游戏内面板尺寸（按按钮数自适应，1920×1080 基准像素 px）**；
    **选择一张背景图片**；下方**两列列出该 mod 全部按钮**，每个按钮可**单独选图**替代数字/文字；
    底部可填**整体透明度（0-100，留空=原图）**；点「继续」后图片自动缩放适配素材尺寸并注入。
- **素材与显示尺寸**：背景/按钮 PNG 是**高清纹理素材**（背景默认 512×256、按钮 256×160 像素）；
  **游戏内显示尺寸由按钮数自动计算**（列数：≤8 个→4 列、≤16→6 列、≤24→8 列，背景高随行数增长），
  素材会被拉伸/缩放到对应显示比例——**面板大小不是写死的，按钮越多面板越高**。
- 自定义图片会复制到 mod 文件夹的 `zz_panel_custom\`（bg.png / 1.png…N.png / opacity.txt），
  **重新注入自动复用**；删除该文件夹再重注入即清除自定义。
- 图片推荐 **PNG 透明背景**；开关按钮 off 态自动半透明变暗。

### 自定义词库（user_dict.json，v2.3+）
- **exe（或 main.py）同目录**的 `user_dict.json`，程序启动自动读取。
  **没有该文件时程序会自动生成一份模板**（含说明，空词条不影响运行），单 exe 用户也能直接编辑自定义。
- 格式（复制 `user_dict.example.json` 修改）：
```json
{
  "_comment": "自定义翻译：words=新增/覆盖词条；ignore=保持原样不翻译的后缀；case_sensitive=自定义词是否区分大小写",
  "words": { "tunv": "臀部", "WODEMINGZI": "我的名字" },
  "ignore": [ "k100", "special_suffix" ],
  "case_sensitive": false
}
```
- `words` **优先于内置**（可覆盖）；`ignore` 原样显示；`case_sensitive=false` 时大小写都命中
  （大写词条也能用小写输入命中）；`_comment` 写在开头说明，**程序忽略不影响运行**。

---

## 目录结构 / Structure

```
PanelTool/
├── src/
│   ├── main.py       # 图形界面（Tkinter，仅标准库）
│   ├── engine.py     # 核心引擎：解析按键/翻译/注入/检测/回滚/按钮调整
│   ├── history.py    # 备份记录与设置（%APPDATA%\WWMI_MOD面板助手）
│   └── i18n.py       # 中英双语文案（含 AI 提示词全文）
├── AI_PROMPT.md      # 给下一个 AI 的完整方法论（工具内可一键复制）
├── dist/
│   └── WWMI_MOD面板助手.exe   # 单文件程序（PyInstaller 打包）
├── user_dict.example.json  # 自定义词库模板（复制为 user_dict.json 使用）
├── README.md
├── requirements.txt  # pyinstaller + pillow
└── build.bat         # 一键打包
```

运行源码：`python src/main.py`（需 `pip install pillow`；打包已内置）。

---

## 自行打包 / Build

```
pip install pyinstaller
build.bat
```

产物在 `dist\WWMI_MOD面板助手.exe`（单文件，无需安装 Python）。

---

## 数据存储 / Data

- 备份记录：`%APPDATA%\WWMI_MOD面板助手\history.json`
- 设置：同目录 `settings.json`（语言、Mod 起始文件夹、调出键）
- 面板备份文件：就在原 ini 旁（`mod.ini.<时间戳>.bak_panel`）
- 清除记录只清列表，不删 .bak 备份

---

## 致谢 / Credits

- 面板机制学习了鸣潮 MOD 社区作者们的实战写法
  以及 3DMigoto 官方变量作用域文档（Global/Namespaced/Local）。
- 本工具只读写 MOD 的 ini 文本（备份 + 注入 + 回滚），不改游戏本体与模型文件；
  请在修改前自行确认 MOD 归属，效果以游戏内实际表现为准。
- 若你修复了新的案例，欢迎按 `AI_PROMPT.md` 的格式追加，让工具一棒接一棒适应更多情况。
