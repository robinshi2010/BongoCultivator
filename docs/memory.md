# 项目记忆 (Project Memory)

## 核心架构 (Core Architecture)
- **GUI Framework**: PyQt6
- **架构模式**: 
    - `PetWindow` (View/Controller): 处理 UI、输入、动画渲染。
    - `Cultivator` (Model): 处理数据逻辑、属性计算、存档管理 (SQLite)。
    - `InputMonitor` & `ActivityRecorder`: 独立线程监控 APM 并持久化记录。
    - `ItemManager` & `EventManager`: 单例管理数据配置 (DB-driven)。

## 已完成功能 (Completed Features)
1. **基础互动**: 
    - 鼠标拖拽移动
    - 鼠标点击播放随机对话
    - 右键菜单 (Context Menu) - 动态境界文案
    - 托盘图标控制 (System Tray) - 悬浮显示详细属性
    - 窗口置顶且不抢占焦点

2. **修仙核心 (Cultivation Core)**:
    - **状态机**: IDLE (闭关), COMBAT (斗法), WORK (历练), READ (悟道) 基于 APM 自动切换。
    - **境界系统**: 炼气 -> 渡劫 (9个大境界), 升级曲线已平衡 (1天 -> 152天)。
    - **物品系统 (Tier 0-8)**: 
        - 9套标准物品 (灵草/元果/丹药) 存入 SQLite。
        - 动态掉落池: 根据当前境界掉落对应物资 (80%同阶, 15%低阶, 5%高阶)。
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

4. **视觉与特效 (Visuals)**:
    - **状态与素材映射**:
        - **基础状态**: `idle` (摸鱼), `walk` (历练), `read` (悟道), `cast` (斗法), `sleep` (睡觉), `drag` (被拖拽)。
        - **`cultivator_alchemy_*.png` (炼丹)**: 分级显示 - Low(Lv0-2), Mid(Lv3-5), High(Lv6-8)。
        - **`tribulation_*.png` (渡劫/飞升)**: 境界突破时的专属异象 (Lv0-2 已实装)。
    - **粒子系统**: 渡劫(雷电)、炼丹(火焰/漩涡)、点击(光点/爱心)、突破成功(金光)。
    - **动画**: 拖拽挣扎、渡劫序列(动画锁)、呼吸浮动。

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
    - `player_status`: 单行记录 (境界, 经验, 灵石, 属性, 时间戳)。
    - `player_inventory`: 背包物品 (FK to definitions)。
    - `item_definitions`: 静态物品配置 (启动时从 Items v2 导入)。
    - `activity_logs_minute`: 分钟级键鼠操作记录。
    - `activity_logs_daily`: (可选) 聚合数据。
- **机制**: 实时/定期 (1min) 写入数据库；支持重置 ("转世")。

## 执行计划与路线图 (Execution Roadmap)

### 已完成 (Completed)
- [x] **[Plan 1: 核心重构](plan1_done.md)** (MVC, 状态机)
- [x] **[Plan 3: 生产力统计](plan3_done.md)** (Activity Recording, Stats UI)
- [x] **[Plan 4: 数值平衡](plan4_done.md)** (Exp Curve, Item Balance)
- [x] **[Plan 5: 秘籍系统](plan5_done.md)** (Cheat Codes)
- [x] **[Plan 6: UI与系统优化](plan6_done.md)** (Tray Info, Drop Balace, Alchemy 2.0)
- [x] **[Plan 7: 数据库迁移](plan7_done.md)** (SQLite Migration, Item Tier 0-8)
- [x] **[Plan 8: 跨平台打包 (macOS)](plan8_done.md)** (PyInstaller .app)
- [x] **[Plan 2 (Phase 6): 视觉增强](plan2_done.md)** (VFX, Animations)
- [x] **[Plan 9: 物品扩充](plan9_done.md)** (110+ items, Sci-Fi Cultivation lore)
- [x] **[Plan 10: 奇遇事件系统](plan10_done.md)** (DB-driven Event Engine, 60+ events)

### 待执行 (Pending / In Progress)

#### 1. 系统深度化 (Priority: Medium)
- [ ] **[Plan 11: 成就系统](plan11.md)**
    - **内容**: 基于生产力数据 (Keys, Clicks) 的成就反馈机制。

#### 2. 遗留任务 from Plan 2/8
- [ ] **Plan 2 (Phase 8)**: 桌面互动 (窗口吸附) / 放置深度化 (灵田)。
- [ ] **Plan 8 (Windows)**: 在 Windows 环境下运行打包脚本。

---
*上次更新时间: 2025-12-25 11:00*
