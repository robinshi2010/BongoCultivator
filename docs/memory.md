# 项目记忆 (Project Memory)

## 核心架构 (Core Architecture)
- **GUI Framework**: PyQt6
- **架构模式**: 
    - `PetWindow` (View/Controller): 处理 UI、输入、动画渲染。
    - `Cultivator` (Model): 处理数据逻辑、属性计算、存档管理 (SQLite)。
    - `InputMonitor` & `ActivityRecorder`: 独立线程监控 APM 并持久化记录。
    - `ItemManager` & `EventManager`: 单例管理数据配置 (DB-driven)。
    - `AchievementManager`: 追踪成就进度、解锁状态及头衔加成。

## 维护工具 (Maintenance Tools)
- `tools/generate_json_assets.py`: 从代码重建 `src/data/` 下缺失的 items/events JSON 文件 (Fix missing data)。
- `tools/fix_inventory_ids.py`: 迁移旧存档 `player_inventory` 中的过期 ID 到新规范 (Fix English names)。
- `tools/optimize_assets.py`: 自动化资源压缩工具，从 assets 目录备份并压缩/缩放图片 (>512px -> 512px)。
- `DataLoader`: 集成在启动流程中，自动检测并修复空数据库。

## 已完成功能 (Completed Features)
1. **基础互动**: 
    - 鼠标拖拽移动
    - 鼠标点击播放随机对话
    - 右键菜单 (Context Menu) - 动态境界文案
    - 托盘图标控制 (System Tray) - 悬浮显示详细属性
    - 窗口置顶且不抢占焦点
    - **统一拖拽**: 所有子窗口 (Inventory, Market, Alchemy, Stats, Talent) 均支持鼠标按住拖拽。

2. **修仙核心 (Cultivation Core)**:
    - **状态机**: IDLE (闭关), COMBAT (斗法), WORK (历练), READ (悟道) 基于 APM 自动切换。
    - **境界系统**: 炼气 -> 渡劫 (9个大境界), 升级曲线已平衡 (1天 -> 152天)。
    - **物品系统 (Tier 0-8)**: 
        - 9套标准物品 (灵草/元果/丹药) 存入 SQLite。
        - 动态掉落池: 根据当前境界掉落对应物资 (80%同阶, 15%低阶, 5%高阶)。
        - **资源闭环**: 为Tier 0-8增加通用采集/挖矿/狩猎事件，确保基础材料稳定产出。
    - **炼丹系统**: 
        - 基于配方的炼丹界面 (`AlchemyWindow`)。
        - 丹药效果: 经验 (1%-5%)、状态恢复、Buff。
    - **秘籍系统 (Cheats)**: 
        - 右键隐藏入口输入密令，快速突破或重置 (`reborn`)。

3. **生产力与统计 (Productivity & Stats)**:
    - **数据采集**: `pynput` 监听键盘鼠标操作量。
    - **持久化**: 分钟级数据存入 SQLite。
    - **可视化**: `StatsWindow` 展示今日/近7天/本月/今年的活跃度趋势 (Matplotlib)。
    - **游戏化**: 努力工作 (高APM) 增加“历练”收益。

4. **视觉与特效**:
*   **混合渲染系统**: `QPixmap` (静态人物) + `EffectWidget` (动态粒子) 分层渲染。
*   **渡劫视觉系统**: 
    *   **独立动画状态**: 实现了 `is_ascending` 锁，确保渡劫动画（3秒）拥有绝对的 Update 优先级，不被 IDLE 状态打断。
    *   **全境界覆盖**: 完成了 Lv0-Lv8 全套渡劫图片素材的生成与集成，支持不同境界显示差异化的渡劫姿态（如气旋、结丹、元神出窍、分身、虚空、飞升等）。
    *   **防御式编程**: 实现了健全的图片回退机制（Fallback）和调试日志，确保资源缺失时不会导致崩溃。
*   **粒子特效**: 实现了 `Tribulation` (雷劫) 和 `Success` (金光) 两套粒子系统，以及透明度修复。
    - **状态与素材映射**:
        - **基础状态**: `idle` (摸鱼), `walk` (历练), `read` (悟道), `cast` (斗法), `sleep` (睡觉), `drag` (被拖拽)。
    - **粒子系统**: 渡劫(雷电)、炼丹(火焰/漩涡)、点击(光点/爱心)、突破成功(金光)。
    - **动画**: 拖拽挣扎、渡劫序列(动画锁, 3s)、呼吸浮动。

5. **成就与头衔 (Achievements & Titles)**:
    - **天道功德**: 追踪累计点击/按键/在线时长，解锁 20+ 个成就。
    - **头衔系统**: 佩戴头衔 (如"筑基·初窥") 获取被动属性加成 (EXP/灵石/掉率)。
    - **UI集成**: `StatsWindow` 新增成就管理页签，实时查看进度与奖励。
    
6. **动态对话 (Dynamic Dialogue)**:
    - **数据库驱动**: `dialogue_definitions` 表存储对话。
    - **上下文感知**: 根据 境界 (Realm 0-8), 心魔 (Mind), 勤勉度 (Clicks) 和 行为状态 (State) 触发不同语音。

7. **事件系统 (Events)**:
    - **分级文案**: 通用事件 (T0-T8) 拥有差异化文案，涵盖山野/秘境/虚空/法则等主题。
    - **权重平衡**: 调整了 Common/Uncommon/Rare/Unique 事件的权重，保证资源获取。
    - **日志系统**: 修复了事件结果显示重复的问题，并在 UI 和数据库中记录单次精确结果。

8. **性能与体积优化 (Optimization)**:
    - **体积瘦身**: 通过移除冗余依赖 (numpy, pandas 等) 和压缩资源，将 macOS 应用包体积从 240MB 降至 125MB。
    - **资源管理**: 实现了资源加载的按需优化 (Scale)。

9. **平台兼容性 (Platform Compatibility)**:
    - **macOS Window Level**: 实现了动态切换窗口层级 (`kCGFloatingWindowLevelKey` vs `kCGNormalWindowLevelKey`) 以修复“始终置顶”功能的开关失效问题。
    - **Tray Sync**: 托盘菜单状态与窗口实际状态 (Notifications) 的双向同步。

## 置顶显示且不影响操作其他软件 (macOS 实现要点)
目标：小人窗口始终在最前端，同时不抢焦点，用户仍可正常操作其他应用。

1. **Qt 窗口属性层**
   - `WindowStaysOnTopHint`：保持置顶。
   - `Tool` + `WindowDoesNotAcceptFocus`：窗口可见但不抢焦点。
   - `WA_ShowWithoutActivating`：显示时不激活应用。
   - `WA_TranslucentBackground` + `background: transparent`：透明背景，避免遮挡。

2. **macOS 原生窗口层级与空间**
   - 通过 `winId()` 获取 `NSWindow`，调用 Objective‑C API 设置：
     - `setLevel(CGWindowLevelForKey(kCGFloatingWindowLevelKey))`：置顶层级。
     - `setCollectionBehavior(CanJoinAllSpaces | Stationary | FullScreenAuxiliary)`：保证跨桌面/全屏应用时仍显示。
     - `setHidesOnDeactivate(False)`：失去激活时也不隐藏。
     - `orderFrontRegardless()`：确保置前。

## 数据存储 (Data Persistence)
- **数据库**: `user_data.db` (SQLite)
- **表结构**:
    - `player_status`: 单行记录 (含 `equipped_title` 字段)。
    - `achievements`: 成就记录 (id, unlocked_at, status)。
    - `player_inventory`: 背包物品 (FK to definitions)。
    - `item_definitions`: 静态物品配置 (启动时从 Items v2 导入)。
    - `activity_logs_minute`: 分钟级键鼠操作记录。
    - `activity_logs_daily`: (可选) 聚合数据。
- **机制**: 实时/定期 (1min) 写入数据库；支持重置 ("转世")。
- **进度迁移 (Plan 46)**: 托盘菜单"轮回转世"支持导出/导入 JSON 格式的完整进度备份，版本无关，解决更新丢档问题。

## 执行计划与路线图 (Execution Roadmap)

### 已完成 (Completed)
- [x] **[Plan 1: 核心重构](plans/archive/plan1_done.md)** (MVC, 状态机)
- [x] **[Plan 3: 生产力统计](plans/archive/plan3_done.md)** (Activity Recording, Stats UI)
- [x] **[Plan 4: 数值平衡](plans/archive/plan4_done.md)** (Exp Curve, Item Balance)
- [x] **[Plan 5: 秘籍系统](plans/archive/plan5_done.md)** (Cheat Codes)
- [x] **[Plan 6: UI与系统优化](plans/archive/plan6_done.md)** (Tray Info, Drop Balace, Alchemy 2.0)
- [x] **[Plan 7: 数据库迁移](plans/archive/plan7_done.md)** (SQLite Migration, Item Tier 0-8)
- [x] **[Plan 8: 跨平台打包 (macOS)](plans/archive/plan8_done.md)** (PyInstaller .app)
- [x] **[Plan 2 (Phase 6): 视觉增强](plans/archive/plan2_done.md)** (VFX, Animations)
- [x] **[Plan 9: 物品扩充](plans/archive/plan9_done.md)** (110+ items, Sci-Fi Cultivation lore)
- [x] **[Plan 10: 奇遇事件系统](plans/archive/plan10_done.md)** (DB-driven Event Engine, 60+ events)
- [x] **[Plan 11: 成就系统](plans/archive/plan11_done.md)** (Achievements, Titles & Buffs)
- [x] **[Plan 13: 渡劫视觉逻辑](plans/archive/plan13_done.md)** (Tribulation Animation Sequence, Transparency)
- [x] **[Plan 12: 视觉素材扩展](plans/archive/plan12_done.md)** (Phase 2 & 3 Tribulation Assets)
- [x] **[Plan 14: 轮回继承](plans/archive/plan14_done.md)** (Legacy System, Death/Rebirth Logic)
- [x] **[Plan 15: 物品价值与经济循环](plans/archive/plan15_done.md)** (Item Utility, Market Selling, Interactive Events)
- [x] **[Plan 17: 经济平衡与事件修复](plans/archive/plan17_done.md)** (Event Logic Fix, Economy Safeguard)
- [x] **[Plan 18: 修复物品使用逻辑](plans/archive/plan18_done.md)** (Fix Pill Consumption, Map Item Types)
- [x] **[Plan 19: 物品使用反馈](plans/archive/plan19_done.md)** (Visual Notifications for Item Usage)
- [x] **[Plan 20: 完善丹药效果](plans/archive/plan20_done.md)** (Inject Effects for Empty Items)
- [x] **[Plan 21: 物品详情优化](plans/archive/plan21_done.md)** (Rich Text Description in UI)
- [x] **[Plan 22: 数据持久化与存档迁移](plans/archive/plan22_done.md)** (Local AppData Storage)
- [x] **[Plan 23: 数据自动同步](plans/archive/plan23_done.md)** (Version Control for Static Data)
- [x] **[Plan 24: 每日奖励修复](plans/archive/plan24_done.md)** (Fix Daily Reward Duplicate Claim)
- [x] **[Plan 26: 坊市刷新机制](plans/archive/plan26_done.md)** (Market Refresh & Dynamic Tier)
- [x] **[Plan 27: 统一窗口拖拽](plans/archive/plan27_done.md)** (Unified Draggable Windows)
- [x] **[Plan 30: 探险与经济平衡](plans/archive/plan30_done.md)** (Economy Rebalance, Generic Resource Events)
- [x] **[Plan 31: 动态对话系统](plans/archive/plan31_done.md)** (Dynamic Dialogue, Context-Aware)
- [x] **[Plan 32: 事件文案差异化](plans/archive/plan32_done.md)** (Rich Event Content, Tier-based)
- [x] **[Plan 29: 坊市体验优化](plans/archive/plan29_done.md)** (Market UX Fixes, Chinese Tiers)
- [x] **[Plan 34: 修复废丹显示](plans/archive/plan34_done.md)** (Fix Pill Waste Translation)
- [x] **[Plan 35: UI与体验优化](plans/archive/plan35_done.md)** (Windows Fixes, Multi-screen, Tray, Logs)
- [x] **[Plan 36: 项目体积优化](plans/archive/plan36_size_optimization_done.md)** (App Size < 150MB, Asset Compression)
- [x] **[Plan 37: 托盘与窗口置顶修复](plans/archive/plan37_tray_fixes_done.md)** (Tray State Sync, macOS Toggle Logic)
- [x] **[Plan 38: 事件日志修复](plans/archive/plan38_event_log_fix_done.md)** (Fix Log Deplication)

### 待执行 (Pending / In Progress)


#### 4. 优化 (Plan 25)
- [x] **[Plan 39: 制作人彩蛋](plans/archive/plan39_creator_easter_egg_done.md)** (Added Creator Easter Egg Dialogues)
- [x] **[Plan 40: 界面与交互修复](plans/archive/plan40_ui_fixes_done.md)** (Replaced MessageBox, Removed MPL)
- [x] **[Plan 41: 修复日志窗口报错](plans/archive/plan41_fix_log_error_done.md)** (Fixed Import Scope)
- [x] **[Plan 42: 修复逻辑 Bug](plans/archive/plan42_fix_app_logic_done.md)** (Safe Resource Consumption)
- [x] **[Plan 43: 炼丹 UI 修复](plans/archive/plan43_fix_alchemy_ui_done.md)** (Sync UI State)
- [x] **[Plan 44: 丹药效果实装](plans/archive/plan44_pills_update.md)** (Updated Pill Effects & Docs)
- [x] **[Plan 45: 气运系统重构](plans/archive/plan45_luck_rework_done.md)** (Luck Overhaul, Per-Life Roguelike Stat)
- [x] **[Plan 46: 进度迁移系统](plans/archive/plan46_progress_migration_done.md)** (轮回转世: 导出/导入 JSON 进度备份)
- [x] **[Plan 47: 代码质量修复](plans/archive/plan47_code_quality_fix_done.md)** (修复重复代码/死代码/魔法数字)
- [x] **[Plan 48: 游戏平衡性调整](plans/archive/plan48_balance_tuning_done.md)** (挂机+200%/坊市15分钟/心魔平衡/丹方优化)
- [ ] **[Plan 25]**: [用户注册与数据留存 (Supabase)](plans/active/plan25.md)

---
(最后更新: 2026-01-10 23:43)
