# -*- coding: utf-8 -*-
"""WWMI MOD 面板助手 - 中英双语字典"""

ZH = {
    "app_title": "WWMI MOD 面板助手",
    "select_mod": "选择 Mod 文件夹",
    "add_panel": "一键添加面板",
    "edit_labels": "修改按钮文字",
    "settings": "设置",
    "rollback_all": "一键回滚全部",
    "clear_records": "清除记录",
    "col_mod": "Mod 名称",
    "col_time": "添加时间",
    "col_method": "方案",
    "col_count": "按钮数",
    "col_key": "面板键",
    "scan_panels": "一键扫描",
    "scan_title": "扫描已注入面板",
    "scan_need_dir": "请先设置 Mod 起始文件夹",
    "scan_need_dir_detail": "一键扫描会扫描设置里的「Mod 起始文件夹」下所有 mod，找到已注入面板的 mod 并恢复备份记录。\n请先在设置中配置 Mod 起始文件夹（通常为 XXMI\\WWMI\\Mods）。",
    "scan_empty": "未扫描到已注入面板的 mod。",
    "scan_done": "扫描完成：找到 {n} 个已注入面板的 mod，已恢复备份记录。",
    "col_status": "状态",
    "no_records": "暂无备份记录",
    "method1": "方案1（含义）",
    "method2": "方案2（编号）",
    "status_ok": "已添加",
    "status_adjusted": "已调整",
    "status_edited": "已改字",
    "select_folder_first": "请先选择 Mod 文件夹",
    "no_keys_found": "未检测到可切换按键",
    "no_keys_detail": "该 Mod 可能没有按键切换配置，或所有按键段都是 UI/鼠标辅助段。\n请确认选择的文件夹内包含角色 Mod 的 .ini 文件（含 [Key...] 段）。",
    "success_title": "添加成功",
    "success_msg": "面板已添加到：{mod}\n按钮数量：{count}\n调出键：{key}\n游戏内按 F10 热重载 MOD 后，按调出键即可开关面板。",
    "fail_title": "添加失败",
    "fail_msg": "无法为 {mod} 添加面板：\n{reason}",
    "fail_retry_method2": "方案1 添加失败。是否自动回滚并改用 方案2（编号按钮）重试？",
    "retry_yes": "是，改用方案2",
    "retry_no": "否，取消",
    "method_pick_title": "选择面板方案",
    "multi_ini_hint": "该 Mod 的按键分布在多个 ini 文件中。>> 标记为推荐项（默认命名空间、按钮最多）；若面板调不出，请选择对应当前游戏模式的那个 ini。",
"method_pick_desc": "请选择按钮标注方式：",
    "method1_desc": "自动读取按键段后缀并翻译成含义\n（如 Keyface → 脸、Keyshoes → 鞋、Keymaoer → 猫耳）\n支持常见拼音/英文部件名；未收录的后缀原样显示，\n可用「修改按钮文字」功能手动修正。",
    "method2_desc": "按钮统一标注为 1、2、3…\n适合后缀无意义的 Mod；\n可用「修改按钮文字」功能设置自己的名称。",
    "btn_use": "使用此方案",
    "preview_label": "按钮预览：",
    "rollback_confirm": "确认回滚 {mod} 的面板？\n将恢复备份并删除生成的面板文件。",
    "rollback_done": "已回滚：{mod}",
    "rollback_all_done": "已回滚全部面板",
    "rollback_all_confirm": "确认回滚全部面板？将恢复所有备份并删除生成的面板文件。",
    "clear_done": "已清除记录列表（备份文件保留）",
    "no_file": "面板配置文件不存在：{path}\n可能已被删除。",
    "adjust_done": "已{action}按钮（{mod}）\n游戏内按 F10 重载生效。",
    "adjust_bigger": "增大",
    "adjust_smaller": "缩小",
    "adjust_taller": "加长",
    "adjust_wider": "加宽",
    "adjust_reset": "重置",
    "menu_rollback": "单独回滚",
    "menu_bigger": "增大面板按钮",
    "menu_smaller": "缩小面板按钮",
    "menu_taller": "加长面板按钮",
    "menu_wider": "加宽面板按钮",
    "menu_reset": "重置面板按钮",
    "menu_open": "打开配置文件",
    "settings_title": "设置",
    "lang_label": "界面语言",
    "lang_zh": "中文",
    "lang_en": "English",
    "save": "保存",
    "cancel": "取消",
    "mod_start_label": "Mod 起始文件夹",
    "mod_start_help": "选择 Mod 文件夹时从此目录开始浏览",
    "mod_start_set": "选择…",
    "toggle_key_label": "面板调出键",
    "toggle_key_help": "默认 /；若被 Mod 占用会自动换字母。A-Z/0-9 支持最稳",
    "custom_images_label": "图片自定义（测试功能）",
    "custom_images_help": "开启后注入面板可选用自定义图片（实验性，可能不完善）",
    "custom_mode_title": "注入方式",
    "custom_mode_desc": "已开启图片自定义，请选择本次注入方式：",
    "custom_mode_btn1": "自定义注入（选图做背景 / 按钮图案）",
    "custom_mode_btn2": "通用注入（默认文字按钮）",
    "custom_title": "自定义面板图片",
    "custom_bg_size": "背景/按钮为高清纹理素材；游戏内尺寸按按钮数自适应（1920×1080 基准约 {pw} × {ph} 像素(px)）",
    "custom_pick_bg": "选择背景图片…",
    "custom_btn_section": "按钮图案（两列；选图会替代数字/文字，留空则用默认文字）",
    "custom_pick_btn": "选图…",
    "custom_opacity": "整体透明度（0-100，留空=原图）",
    "custom_fill": "按钮自适应填充面板（勾选=按钮自动变大铺满；不勾选=默认大小居中）",
    "custom_total": "按钮总数：{n}",
    "custom_cols": "每行按钮数",
    "custom_rows": "行数（自动）：{r}",
    "custom_cols_hint": "调每行按钮数后行数自动变化（1-9）",
    "custom_continue": "继续",
    "about": "关于",
    "about_text": "WWMI MOD 面板助手 v2.0（注入式）\n\n读取 Mod 的按键配置，生成快捷切换面板并注入 Mod 自身 ini。\n样式1：单页全部按钮（唯一验收方案）。\n面板透明、可拖动、可一键调整大小、可改按钮文字。",
    "ai_prompt": "AI 修复提示词",
    "ai_prompt_title": "AI 修复提示词（复制给 AI 继续排查/完善）",
    "ai_prompt_hint": "一键修复不一定一次成功。把下面这份方法论连同你的 MOD 情况发给任意 AI，AI 能顺着已验证的思路继续排查与修复；成功修复新案例后，请按文末格式追加到本工具与 README，让它一棒接一棒适应更多情况。",
    "ai_copy": "复制全部",
    "ai_copied": "提示词已复制到剪贴板，可粘贴发给任意 AI。",
    "first_lang_title": "选择语言 / Choose Language",
    "first_dir_title": "选择 Mod 文件夹 / Choose Mod Folder",
    "first_dir_desc": "选择你的 Mods 目录（通常为 XXMI\\WWMI\\Mods），\n之后选择 Mod 时会从这里开始浏览（可在设置中修改）。",
    "first_dir_skip": "跳过（稍后可在设置中修改）",
    "close": "关闭",
    "learn_more": "了解更多",
    "error_title": "出错了",
    "learn_detail": "详细说明",
    "lang_saved": "语言已切换，重启界面后完全生效。",
    "processing": "处理中，请稍候…",
    "need_select_for_adjust": "请先在记录列表中选择一个已添加面板的 Mod",
    "record_gone": "该 Mod 的记录已不存在（文件可能已被删除）",
    "record_gone_detail": "记录指向的 ini 不存在。\n可能原因：1) 该面板已被手动删除；2) Mod 目录被移动。\n可在记录列表中删除此记录。",
    "generated_files": "生成文件",
    "open_folder": "打开 Mod 文件夹",
    "panel_exists": "该 Mod 已有面板（已注入）",
    "panel_exists_detail": "检测到 {path} 已注入面板。\n如需重新添加请先回滚现有面板。",
    "bad_dir": "无法读取该文件夹",
    "bad_dir_detail": "请选择包含角色 Mod .ini 配置的文件夹。",
    "learn_usage_title": "使用方法",
    "learn_usage": "1. 选择 Mod 文件夹（含 .ini 与 Textures/ 的目录）\n2. 点「一键添加面板」，选方案后自动注入\n3. 游戏内按 F10 热重载 MOD（无需退出游戏）\n4. 按调出键开关面板；点按钮即触发对应切换\n\n面板说明：\n- 顶部空白条可按住拖动面板；右上角 X 关闭\n- 按钮按下即切换对应部件（开关型按钮 off 时变暗）\n- 备份记录里可回滚/调整按钮大小/改文字\n\n快捷键参考：\nF6 = 切换全部 MOD 开关（隐藏≠不加载）\nF8 = 转储模型帧（FrameAnalysis-* 到 WWMI 目录）\nF10 = 热重载 MOD",
    "learn_usage_en": "1. Select the Mod folder (contains .ini and Textures/)\n2. Click Add Panel, pick a method, it injects automatically\n3. Press F10 in game to hot-reload MODs (no need to quit)\n4. Press the toggle key to show/hide the panel; click a button to trigger the toggle\n\nPanel notes:\n- Drag the panel by the top blank bar; close with the X on top-right\n- Clicking a button toggles that part (toggle buttons dim when off)\n- In the backup list you can rollback / resize buttons / rename labels",
    "edit_title": "修改按钮文字",
    "edit_desc": "修改按钮显示文字（每行一个，回车分隔）：",
    "edit_apply": "应用并重新生成",
    "edit_done": "按钮文字已更新，游戏内按 F10 重载生效。",
    "edit_fail": "修改按钮文字失败：\n{reason}",
    "no_panel_record": "该记录没有面板（ini 未注入或已回滚）",
    "toggle_auto": "自动选择（避开 Mod 已用键）",
    "ok": "确定",
    "yes": "是",
    "no": "否",
    "ai_prompt_text": """WWMI MOD 面板助手 - AI 修复提示词 v2
（把下面全部内容 + 你的 MOD 情况发给任意 AI，AI 可顺着已验证思路继续排查与修复）

【工具定位】
读取鸣潮(WuWa) MOD 的 [Key...] 按键配置，自动生成透明快捷切换面板并注入该 MOD 自身的 ini。
面板按钮 = 一个 Key 段（多取值 = 同一按钮轮播切换）；调出键默认 /。
游戏内按 F10 热重载 MOD（无需退出游戏）；按调出键开关面板，点按钮即触发对应切换。

【3DMigoto 变量作用域核心规则（官方，务必牢记）】
1. 变量：global $x = 所有命名空间/CommandList 可见；global persist $x = 同上且存档 d3dx_user.ini；
   $\\ns\\x = 仅该命名空间；$x（无前缀）= 仅当前 CommandList 作用域（Local）。
2. Key 段（原按键）在按键事件的全局上下文执行，无前缀赋值命中全局变量 → 跨文件有效。
3. CommandList（面板按钮走的通道）里无前缀赋值 $var = 值 → 只落在该 CommandList 所在 ini 的作用域，不跨文件。
   → 面板按钮要改的变量属于哪个 override，面板就必须注入到该 override 所在的 ini（同文件）。
4. [Present] 每帧执行；post 前缀 = Present 后执行；面板绘制链（[Present] if $zz_open → run Draw → 贴图资源）
   与检测变量必须同一文件才能联动。
5. hash 匹配：TextureOverride 按 hash 匹配游戏 draw；同一 ini 内同 hash 多段可能存在"首个消费"，
   检测段放同 hash 竞争多的文件会匹配不到 draw → 检测变量恒 0 → 面板调不出。

【已验证样式1 结构（禁止改回样式2/分页）】
[Constants] 声明 $zz_open/$zz_clicked/$zz_holded/$zz_cx/$zz_cy/$zz_lastx/$zz_lasty/$zz_ww/$zz_wh/$zz_ar/
$zz_fx/$zz_fy/$zz_bw/$zz_bh/$zz_gap/$zz_pad/$zz_title_h/$zz_close_w/$zz_cols/$zz_btns/$zz_pw/$zz_ph
[KeyToggleZZUI] condition=<检测> key=<调出键> type=cycle $zz_open=0,1
[KeyMouseZZ] condition=$zz_open key=VK_LBUTTON type=hold $zz_holded=1 $zz_clicked=1
[Present] post $zz_detected=0（self 检测时）；if $zz_open { run Init; run Draw; $zz_clicked=0 }
[CommandListZZInit] 取窗口/渲染目标分辨率 → $zz_ww/$zz_wh/$zz_ar；取鼠标坐标 → $zz_cx/$zz_cy
[CommandListZZDraw] x87/y87/z87/w87 画背景/标题/关闭钮/各按钮；按钮 ps-t100 切 on/off 图
[CommandListZZBtnN] 鼠标在按钮区 && $zz_clicked → run ToggleN；ps-t100=BtnN on/off
[CommandListZZToggleN] 按钮变量轮播（一 Key 段=一按钮，多值轮播）
拖动：单 [KeyMouseZZ] hold 置 $zz_holded/$zz_clicked；[Present] 不归零 holded；[CommandListZZDrag] 增量拖动+边界 clamp（验收版，禁止改动）
资源：zz_panel_res\\btn_N.png（on）/btn_N_off.png；标签 zz_panel_labels.json

【人物检测（面板只在对应角色可调出）】
- reuse：mod 已有检测变量（$active/$object_detected 等，在 Key 段 condition 使用且有置位）→ 面板 Key condition 用它。
  ⚠ 该变量必须与面板所在 ini 同一文件置位/读取，否则跨文件读不到（露帕 cutscene 注入 $object_detected 调不出）。
- self：mod 无检测变量 → 自建 [TextureOverrideZZDetect]（复用人物网格 hash + match_first_index）→ 命中置 $zz_detected=1，Present post 归零。
  ⚠ ZZDetect 必须与 KeyToggleZZUI 同文件（$zz_detected 无前缀赋值=文件级），且放同 hash 竞争少的 ini。
- none：无条件（任何角色可调出）——仅测试用。

【多 ini / 多形态 Mod（重要）】
- 多形态=多 ini（cutscene/playable/tail 等），同名变量各自独立（无前缀=文件级）。
- 面板必须注入 override 所在文件（按钮赋值才生效）；调出检测链（Key+检测+Present）也必须与面板同文件。
- 已知失败案例【露帕 Lupa】：cutscene/playable/tail 三文件 + tail_controller（namespace=lupa\\Master）。
  · 注入 cutscene：面板能调出（检测/绘制链同文件 OK）但按钮 2-8 无效（CommandList 赋值 $proportions 落在 cutscene，
    playable 的 override 读不到）；仅 Swap（$\\lupa\\Master\\swapvar 显式跨 ns）有效。
  · 注入 playable：按钮上下文正确，但面板连无条件 Key 都调不出（ZZDetect 放 playable 同 hash 竞争匹配不到；
    ZZDetect 放 cutscene 则 $zz_detected 赋值跨文件失效；condition 用 $object_detected 也调不出）——未解决，留给下一个 AI：
    用 F8 转储（角色界面/开启 mod）比对 log.txt 确认 playable 网格 hash 命中与 draw 顺序；尝试把整个面板
    （Key+Present+CommandList+资源+检测）全部集中到 playable 同一文件并核对 [Present] 与 mod 自带 [Present]
    合并结构（if/endif 配对）；或把露帕类（多形态+namespace 混用）mod 明确标注"不支持"。
- 已确认可用：守岸人（self 检测 0266ab77）、尤诺（reuse $active==1）、绯雪/达妮娅（作者原生面板，段名不撞即常态可用）。

【排查方法论（按钮/面板失效时）】
1. 区分层：点按钮有无反馈（on/off 图切换）？
   - 无反馈 = 点击没触发（$zz_clicked/鼠标区域/KeyMouse 问题）
   - 有反馈但功能没变 = 赋值执行了但 override 没读到（作用域/文件问题——最可能）
2. 原按键对比：原按键有效而面板无效 = CommandList 赋值作用域问题（面板不在 override 同文件）。
3. 面板调不出：先无条件（删 condition）测 Key 触发；再查 [Present] 合并结构与检测变量置位；再查调出键是否被占用。
4. 一切改动前备份；F10 热重载测试；逐项记录。

【可持续更新】
修复好新案例后，按「多 ini/多形态」格式追加到本提示词与 README（Mod 名/形态结构/根因/修法），
让工具与提示词一棒接一棒适应更多情况。""",
}

EN = {
    "app_title": "WWMI MOD Panel Helper",
    "select_mod": "Select Mod Folder",
    "add_panel": "Add Panel",
    "edit_labels": "Edit Button Labels",
    "settings": "Settings",
    "rollback_all": "Rollback All",
    "clear_records": "Clear Records",
    "col_mod": "Mod Name",
    "col_time": "Added At",
    "col_method": "Method",
    "col_count": "Buttons",
    "col_key": "Panel Key",
    "scan_panels": "Scan Injected",
    "scan_title": "Scan Injected Panels",
    "scan_need_dir": "Set the Mod start folder first",
    "scan_need_dir_detail": "Scan looks under the Mod start folder (set in Settings) for all mods with an injected panel and restores their backup records.\nConfigure the Mod start folder in Settings first (usually XXMI\\WWMI\\Mods).",
    "scan_empty": "No injected panels found.",
    "scan_done": "Scan complete: found {n} mod(s) with injected panels, backup records restored.",
    "col_status": "Status",
    "no_records": "No backup records",
    "method1": "Method 1 (Names)",
    "method2": "Method 2 (Numbers)",
    "status_ok": "Added",
    "status_adjusted": "Adjusted",
    "status_edited": "Renamed",
    "select_folder_first": "Please select a Mod folder first",
    "no_keys_found": "No toggleable keys found",
    "no_keys_detail": "This Mod may have no key-toggle config, or all [Key...] sections are UI/mouse helpers.\nMake sure the selected folder contains the character Mod .ini files (with [Key...] sections).",
    "success_title": "Panel Added",
    "success_msg": "Panel added to: {mod}\nButtons: {count}\nToggle key: {key}\nPress F10 in game to hot-reload MODs, then press the toggle key.",
    "fail_title": "Failed",
    "fail_msg": "Cannot add panel to {mod}:\n{reason}",
    "fail_retry_method2": "Method 1 failed. Auto-rollback and retry with Method 2 (numbered buttons)?",
    "retry_yes": "Yes, use Method 2",
    "retry_no": "No, cancel",
    "method_pick_title": "Choose Panel Method",
    "multi_ini_hint": "Keys of this Mod are split across multiple ini files. >> marks the recommended entry (default namespace, most buttons); if the panel won't show, pick the ini matching your current game mode.",
"method_pick_desc": "Choose how buttons are labeled:",
    "method1_desc": "Read the key-section suffix and translate it\n(e.g. Keyface → Face, Keyshoes → Shoes, Keymaoer → Cat ears)\nCommon pinyin/English part names are covered; unknown suffixes are shown as-is\nand can be fixed with \"Edit Button Labels\".",
    "method2_desc": "Label buttons as 1, 2, 3…\nFor Mods without meaningful suffixes.\nYou can rename buttons with \"Edit Button Labels\".",
    "btn_use": "Use This Method",
    "preview_label": "Button preview: ",
    "rollback_confirm": "Roll back panel for {mod}?\nThe backup will be restored and generated files removed.",
    "rollback_done": "Rolled back: {mod}",
    "rollback_all_done": "All panels rolled back",
    "rollback_all_confirm": "Roll back ALL panels? All backups will be restored and generated files removed.",
    "clear_done": "Records cleared (backup files kept)",
    "no_file": "Panel config not found: {path}\nIt may have been deleted.",
    "adjust_done": "Buttons {action} ({mod})\nPress F10 in game to reload.",
    "adjust_bigger": "Bigger",
    "adjust_smaller": "Smaller",
    "adjust_taller": "Taller",
    "adjust_wider": "Wider",
    "adjust_reset": "Reset",
    "menu_rollback": "Rollback",
    "menu_bigger": "Make Buttons Bigger",
    "menu_smaller": "Make Buttons Smaller",
    "menu_taller": "Make Buttons Taller",
    "menu_wider": "Make Buttons Wider",
    "menu_reset": "Reset Button Size",
    "menu_open": "Open Config File",
    "settings_title": "Settings",
    "lang_label": "Language",
    "lang_zh": "中文",
    "lang_en": "English",
    "save": "Save",
    "cancel": "Cancel",
    "mod_start_label": "Mod Start Folder",
    "mod_start_help": "Folder where Mod-folder browsing starts",
    "mod_start_set": "Choose…",
    "toggle_key_label": "Panel Toggle Key",
    "toggle_key_help": "Default /; switches to a letter if taken by the Mod. A-Z/0-9 are most reliable",
    "custom_images_label": "Custom Images (Beta)",
    "custom_images_help": "Pick custom images for panel background/buttons (experimental)",
    "custom_mode_title": "Injection Mode",
    "custom_mode_desc": "Custom images is enabled. Choose injection mode:",
    "custom_mode_btn1": "Custom inject (pick images for bg/buttons)",
    "custom_mode_btn2": "Normal inject (default text buttons)",
    "custom_title": "Custom Panel Images",
    "custom_bg_size": "Textures are hi-res; in-game size auto-fits button count (~{pw} × {ph} px at 1920×1080)",
    "custom_pick_bg": "Pick background image...",
    "custom_btn_section": "Button images (two columns; picking an image replaces text, empty = text)",
    "custom_pick_btn": "Pick...",
    "custom_opacity": "Overall opacity (0-100, empty = original)",
    "custom_fill": "Auto-fill buttons (checked = buttons grow to fill; unchecked = default size centered)",
    "custom_total": "Total buttons: {n}",
    "custom_cols": "Buttons per row",
    "custom_rows": "Rows (auto): {r}",
    "custom_cols_hint": "Rows auto-adjust when you change buttons per row (1-9)",
    "custom_continue": "Continue",
    "about": "About",
    "about_text": "WWMI MOD Panel Helper v2.0 (injection)\n\nReads a Mod's key config and injects a quick-toggle panel into the Mod's own ini.\nStyle 1: single page with all buttons (the only accepted style).\nTransparent panel, draggable, one-click resize, editable button labels.",
    "first_lang_title": "选择语言 / Choose Language",
    "first_dir_title": "选择 Mod 文件夹 / Choose Mod Folder",
    "first_dir_desc": "Select your Mods folder (usually XXMI\\WWMI\\Mods).\nMod-folder browsing will start from here (editable in Settings).",
    "first_dir_skip": "Skip (change later in Settings)",
    "close": "Close",
    "learn_more": "Learn More",
    "error_title": "Error",
    "learn_detail": "Details",
    "lang_saved": "Language switched. Restart for full effect.",
    "processing": "Working, please wait…",
    "need_select_for_adjust": "Select a Mod record with a panel first",
    "record_gone": "The record's panel file no longer exists",
    "record_gone_detail": "The ini this record points to does not exist.\nPossible causes: 1) the panel was deleted manually; 2) the Mod folder was moved.\nYou may delete this record from the list.",
    "generated_files": "Generated Files",
    "open_folder": "Open Mod Folder",
    "panel_exists": "This Mod already has a panel (injected)",
    "panel_exists_detail": "{path} already has an injected panel.\nRoll it back first if you want to re-add.",
    "bad_dir": "Cannot read this folder",
    "bad_dir_detail": "Please choose a folder containing the character Mod .ini files.",
    "learn_usage_title": "How to Use",
    "learn_usage": "1. Select the Mod folder (contains .ini and Textures/)\n2. Click Add Panel, pick a method, it injects automatically\n3. Press F10 in game to hot-reload MODs (no need to quit)\n4. Press the toggle key to show/hide the panel; click a button to trigger the toggle\n\nPanel notes:\n- Drag the panel by the top blank bar; close with the X on top-right\n- Clicking a button toggles that part (toggle buttons dim when off)\n- In the backup list you can rollback / resize buttons / rename labels",
    "learn_usage_en": "1. Select the Mod folder (contains .ini and Textures/)\n2. Click Add Panel, pick a method, it injects automatically\n3. Press F10 in game to hot-reload MODs (no need to quit)\n4. Press the toggle key to show/hide the panel; click a button to trigger the toggle\n\nPanel notes:\n- Drag the panel by the top blank bar; close with the X on top-right\n- Clicking a button toggles that part (toggle buttons dim when off)\n- In the backup list you can rollback / resize buttons / rename labels",
    "edit_title": "Edit Button Labels",
    "edit_desc": "Edit button text (one per line, separated by Enter):",
    "edit_apply": "Apply & Regenerate",
    "edit_done": "Button labels updated. Press F10 in game to reload.",
    "edit_fail": "Failed to edit button labels:\n{reason}",
    "no_panel_record": "This record has no panel (ini not injected or already rolled back)",
    "toggle_auto": "Auto (avoid keys used by the Mod)",
    "ok": "OK",
    "yes": "Yes",
    "no": "No",
    "ai_prompt": "AI Repair Prompt",
    "ai_prompt_title": "AI Repair Prompt (copy to an AI to continue debugging / improving)",
    "ai_prompt_hint": "One-click repair may not always succeed first try. Send the methodology below together with your MOD situation to any AI - it can continue debugging along the proven lines. After fixing a new case, append it to this tool and the README in the format at the end.",
    "ai_copy": "Copy All",
    "ai_copied": "Prompt copied to clipboard - paste it to any AI.",
    "ai_prompt_text": """WWMI MOD Panel Helper - AI Repair Prompt v2
(Copy everything below + your MOD situation to any AI; it can continue debugging along the proven lines)

[Tool purpose]
Reads a WuWa MOD's [Key...] config and injects a transparent quick-toggle panel into the MOD's own ini.
One panel button = one Key section (multiple values = the same button cycles through them); default toggle key /.
Press F10 in game to hot-reload MODs (no need to quit); press the toggle key to show/hide the panel; click a button to trigger the toggle.

[3DMigoto variable-scope core rules (official, keep in mind)]
1. Variables: global $x = visible in all namespaces/command lists; global persist $x = same + saved to d3dx_user.ini;
   $\\ns\\x = that namespace only; $x (no prefix) = current command-list scope only (Local).
2. Key sections (original hotkeys) run in the global context of key events; prefix-less assignment hits the global variable -> works across files.
3. CommandList (the channel panel buttons use): prefix-less assignment $var = value lands only in the scope of the ini file that owns this CommandList, NOT across files.
   -> For a panel button to change a variable, the panel MUST be injected into the ini that owns the override reading that variable (same file).
4. [Present] runs every frame; post prefix = runs after Present; the panel's draw chain ([Present] if $zz_open -> run Draw -> textures)
   must be in the same file as the detection variable to work together.
5. hash matching: TextureOverride matches game draws by hash; multiple sections with the same hash in one ini may be "first-consumed",
   so a detection section placed in a file crowded with the same hash may never match a draw -> detection variable stays 0 -> panel won't show.

[Proven Style-1 structure (do NOT revert to Style-2/paging)]
[Constants] declares $zz_open/$zz_clicked/$zz_holded/$zz_cx/$zz_cy/$zz_lastx/$zz_lasty/$zz_ww/$zz_wh/$zz_ar/
$zz_fx/$zz_fy/$zz_bw/$zz_bh/$zz_gap/$zz_pad/$zz_title_h/$zz_close_w/$zz_cols/$zz_btns/$zz_pw/$zz_ph
[KeyToggleZZUI] condition=<detect> key=<toggle> type=cycle $zz_open=0,1
[KeyMouseZZ] condition=$zz_open key=VK_LBUTTON type=hold $zz_holded=1 $zz_clicked=1
[Present] post $zz_detected=0 (self detect); if $zz_open { run Init; run Draw; $zz_clicked=0 }
[CommandListZZInit] read window/render-target size -> $zz_ww/$zz_wh/$zz_ar; read mouse -> $zz_cx/$zz_cy
[CommandListZZDraw] x87/y87/z87/w87 draw bg/title/close/buttons; ps-t100 switches on/off image
[CommandListZZBtnN] mouse in button area && $zz_clicked -> run ToggleN; ps-t100=BtnN on/off
[CommandListZZToggleN] cycles the button variable (one Key section = one button, multi-value cycle)
Drag: single [KeyMouseZZ] hold sets $zz_holded/$zz_clicked; [Present] does NOT reset holded; [CommandListZZDrag] delta-drag + edge clamp (accepted version, do not change)
Resources: zz_panel_res\\btn_N.png (on)/btn_N_off.png; labels zz_panel_labels.json

[Character detection (panel shows only for the matching character)]
- reuse: the MOD already has a detection variable ($active/$object_detected etc., used in Key conditions and assigned somewhere) -> use it in the panel Key condition.
  ! This variable must be assigned AND read in the SAME ini as the panel, otherwise cross-file reads fail (Lupa: cutscene injection with $object_detected would not show).
- self: MOD has none -> create [TextureOverrideZZDetect] (reuse the character mesh hash + match_first_index) -> sets $zz_detected=1 on hit, Present post resets.
  ! ZZDetect must live in the SAME ini as KeyToggleZZUI ($zz_detected prefix-less assignment is file-scoped) and in a file with few same-hash competitors.
- none: unconditional (any character can open) - test only.

[Multi-ini / multi-form MODs (important)]
- Multiple forms = multiple inis (cutscene/playable/tail etc.); same-named variables are independent (prefix-less = file scope).
- The panel MUST be injected into the ini that owns the overrides (so button assignments work); the detect chain (Key+detect+Present) must be in the same file too.
- Known failed case [Lupa]: cutscene/playable/tail three files + tail_controller (namespace=lupa\\Master).
  · Injected into cutscene: panel shows (detect/draw chain same file OK) but buttons 2-8 do nothing (CommandList assigns $proportions in cutscene,
    playable overrides never see it); only Swap ($\\lupa\\Master\\swapvar explicit cross-ns) works.
  · Injected into playable: button scope correct, but even an unconditional Key won't show the panel (ZZDetect inside playable loses the same-hash race;
    ZZDetect in cutscene fails because $zz_detected assignment is cross-file; condition=$object_detected also fails) - unresolved, left for the next AI:
    F8 dump (character screen / MOD on) and check log.txt for playable mesh hash hits and draw order; try placing the ENTIRE panel
    (Key+Present+CommandList+resources+detect) inside playable in one file and verify the [Present] merge with the MOD's own [Present] (if/endif pairing);
    or mark Lupa-like MODs (multi-form + mixed namespaces) as "unsupported".
- Confirmed working: Shorekeeper (self detect 0266ab77), Iuno (reuse $active==1), Feixue/Denia (author-native panels work as long as section names don't collide).

[Troubleshooting methodology (when buttons/panel fail)]
1. Layer split: does clicking a button give feedback (on/off image switch)?
   - No feedback = click did not trigger ($zz_clicked/mouse region/KeyMouse issue)
   - Feedback but nothing changed = assignment ran but the override never read it (scope/file issue - most likely)
2. Compare with the original key: original key works but panel doesn't = CommandList assignment scope issue (panel not in the override's file).
3. Panel won't show: first remove the condition (unconditional) to test Key firing; then inspect the [Present] merge structure and detection variable assignment; then check the toggle key isn't taken.
4. Back up before any change; test with F10 hot-reload; log everything.

[Sustainable updates]
After fixing a new case, append it to this prompt and the README in the "multi-ini/multi-form" format
(Mod name / form structure / root cause / fix), so the tool and prompt keep adapting case by case.""",
}


def get_dict(lang):
    return ZH if lang == "zh" else EN
