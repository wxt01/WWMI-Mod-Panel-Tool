# WWMI MOD 面板助手 - AI 修复提示词 v2

> 把下面全部内容 + 你的 MOD 情况发给任意 AI，AI 可顺着已验证思路继续排查与修复。
> 成功修复新案例后，请按文末格式追加到本文件与 README。

## 工具定位

读取鸣潮(WuWa) MOD 的 `[Key...]` 按键配置，自动生成透明快捷切换面板并注入该 MOD 自身的 ini。
面板按钮 = 一个 Key 段（多取值 = 同一按钮轮播切换）；调出键默认 `\`。
游戏内按 F10 热重载 MOD（无需退出游戏）；按调出键开关面板，点按钮即触发对应切换。

## 3DMigoto 变量作用域核心规则（官方，务必牢记）

1. 变量：`global $x` = 所有命名空间/CommandList 可见；`global persist $x` = 同上且存档 d3dx_user.ini；
   `$\ns\x` = 仅该命名空间；`$x`（无前缀）= 仅当前 CommandList 作用域（Local）。
2. Key 段（原按键）在按键事件的全局上下文执行，无前缀赋值命中全局变量 → 跨文件有效。
3. CommandList（面板按钮走的通道）里无前缀赋值 `$var = 值` → 只落在该 CommandList 所在 ini 的作用域，不跨文件。
   → 面板按钮要改的变量属于哪个 override，面板就必须注入到该 override 所在的 ini（同文件）。
4. `[Present]` 每帧执行；`post` 前缀 = Present 后执行；面板绘制链（[Present] if $zz_open → run Draw → 贴图资源）
   与检测变量必须同一文件才能联动。
5. hash 匹配：TextureOverride 按 hash 匹配游戏 draw；同一 ini 内同 hash 多段可能存在"首个消费"，
   检测段放同 hash 竞争多的文件会匹配不到 draw → 检测变量恒 0 → 面板调不出。

## 已验证样式1 结构（禁止改回样式2/分页）

```
[Constants]             # 声明 $zz_open/$zz_clicked/$zz_holded/$zz_cx/$zz_cy/$zz_lastx/$zz_lasty/
                        # $zz_ww/$zz_wh/$zz_ar/$zz_fx/$zz_fy/$zz_bw/$zz_bh/$zz_gap/$zz_pad/
                        # $zz_title_h/$zz_close_w/$zz_cols/$zz_btns/$zz_pw/$zz_ph
[KeyToggleZZUI]         # condition=<检测> key=<调出键> type=cycle $zz_open=0,1
[KeyMouseZZ]            # condition=$zz_open key=VK_LBUTTON type=hold $zz_holded=1 $zz_clicked=1
[Present]               # post $zz_detected=0（self 检测时）；if $zz_open { run Init; run Draw; $zz_clicked=0 }
[CommandListZZInit]     # 取窗口/渲染目标分辨率 → $zz_ww/$zz_wh/$zz_ar；取鼠标坐标 → $zz_cx/$zz_cy
[CommandListZZDraw]     # x87/y87/z87/w87 画背景/标题/关闭钮/各按钮；ps-t100 切 on/off 图
[CommandListZZBtnN]     # 鼠标在按钮区 && $zz_clicked → run ToggleN；ps-t100=BtnN on/off
[CommandListZZToggleN]  # 按钮变量轮播（一 Key 段=一按钮，多值轮播）
[CommandListZZDrag]     # 增量拖动+边界 clamp（验收版，禁止改动）
```

资源：`zz_panel_res\btn_N.png`（on）/`btn_N_off.png`；标签 `zz_panel_labels.json`。

拖动结构（验收版，禁止再改）：单 `[KeyMouseZZ]` hold 置 `$zz_holded/$zz_clicked`；
`[Present]` 不归零 holded；`[CommandListZZDrag]` 增量拖动 + 边界 clamp。

## 人物检测（面板只在对应角色可调出）

- **reuse**：mod 已有检测变量（`$active/$object_detected` 等，在 Key 段 condition 使用且有置位）→ 面板 Key condition 用它。
  ⚠ 该变量必须与面板所在 ini 同一文件置位/读取，否则跨文件读不到（露帕 cutscene 注入 `$object_detected` 调不出）。
- **self**：mod 无检测变量 → 自建 `[TextureOverrideZZDetect]`（复用人物网格 hash + `match_first_index`）→ 命中置 `$zz_detected=1`，Present post 归零。
  ⚠ ZZDetect 必须与 KeyToggleZZUI 同文件（`$zz_detected` 无前缀赋值=文件级），且放同 hash 竞争少的 ini。
- **none**：无条件（任何角色可调出）——仅测试用。

## 多 ini / 多形态 Mod（重要）

- 多形态=多 ini（cutscene/playable/tail 等），同名变量各自独立（无前缀=文件级）。
- 面板必须注入 override 所在文件（按钮赋值才生效）；调出检测链（Key+检测+Present）也必须与面板同文件。

### 已知失败案例【露帕 Lupa】：cutscene/playable/tail 三文件 + tail_controller（namespace=lupa\Master）

| 尝试 | 结果 |
|---|---|
| 注入 cutscene | 面板能调出（检测/绘制链同文件 OK）但按钮 2-8 无效（CommandList 赋值 `$proportions` 落在 cutscene，playable 的 override 读不到）；仅 Swap（`$\lupa\Master\swapvar` 显式跨 ns）有效 |
| 注入 playable | 按钮上下文正确，但面板连无条件 Key 都调不出（ZZDetect 放 playable 同 hash 竞争匹配不到；ZZDetect 放 cutscene 则 `$zz_detected` 赋值跨文件失效；condition 用 `$object_detected` 也调不出） |

未解决，留给下一个 AI：
用 F8 转储（角色界面/开启 mod）比对 log.txt 确认 playable 网格 hash 命中与 draw 顺序；
尝试把整个面板（Key+Present+CommandList+资源+检测）全部集中到 playable 同一文件并核对 [Present] 与 mod 自带 [Present] 合并结构（if/endif 配对）；
或把露帕类（多形态+namespace 混用）mod 明确标注"不支持"。

已确认可用：守岸人（self 检测 0266ab77）、尤诺（reuse `$active==1`）、绯雪/达妮娅（作者原生面板，段名不撞即常态可用）。

## 排查方法论（按钮/面板失效时）

1. **区分层**：点按钮有无反馈（on/off 图切换）？
   - 无反馈 = 点击没触发（`$zz_clicked`/鼠标区域/KeyMouse 问题）
   - 有反馈但功能没变 = 赋值执行了但 override 没读到（**作用域/文件问题——最可能**）
2. **原按键对比**：原按键有效而面板无效 = CommandList 赋值作用域问题（面板不在 override 同文件）。
3. **面板调不出**：先无条件（删 condition）测 Key 触发；再查 [Present] 合并结构与检测变量置位；再查调出键是否被占用。
4. 一切改动前备份；F10 热重载测试；逐项记录。

## 可持续更新

修复好新案例后，按「多 ini/多形态」格式追加到本提示词与 README
（Mod 名/形态结构/根因/修法），让工具与提示词一棒接一棒适应更多情况。
