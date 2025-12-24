# 项目记忆 (Project Memory)

## 核心架构 (Core Architecture)
- **GUI Framework**: PyQt6
- **架构模式**: 
    - `PetWindow` (View/Controller): 处理 UI、输入、动画渲染。
    - `Cultivator` (Model): 处理数据逻辑、属性计算、存档管理。
    - `InputMonitor`: 独立线程监控 APM。
    - `ItemManager` & `EventManager`: 单例管理数据配置。

## 已完成功能 (Completed Features)
1. **基础互动**: 
    - 鼠标拖拽移动
    - 鼠标点击播放随机对话
    - 右键菜单 (Context Menu)
    - 托盘图标控制 (System Tray)
    - 窗口置顶且不抢占焦点

2. **修仙核心 (Cultivation Core)**:
    - **状态机**: IDLE (闭关), COMBAT (斗法), WORK (历练), READ (悟道) 基于 APM 自动切换。
    - **三维属性**: 
        - `Mind` (心魔): 影响修炼效率与渡劫成功率。
        - `Body` (体魄): 影响渡劫成功率。
        - `Affection` (好感): 影响掉落率。
    - **物品系统**: 
        - 物品分级 (Tier 1-2), 包含材料、消耗品、丹药。
        - 存/取/使用逻辑 (`InventoryWindow`)。
    - **炼丹系统**: 
        - 基于配方的炼丹界面 (`AlchemyWindow`)。
    - **随机事件**:
        - 定时触发 (默认 5分钟)，包含资源获取、状态变更。
    - **渡劫与天赋**:
        - 经验满后需手动渡劫 (成功率受属性影响)。
        - 渡劫成功获得天赋点，可升级 `Exp` (悟性) 或 `Drop` (机缘)。
        - `TalentWindow` 展示属性与加点。
    - **坊市系统**: 
        - 每日或手动刷新的随机商店。

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
     - `setCollectionBehavior(CanJoinAllSpaces | Stationary | FullScreenAuxiliary)`：
       保证跨桌面/全屏应用时仍显示。
     - `setHidesOnDeactivate(False)`：失去激活时也不隐藏。
     - `orderFrontRegardless()`：确保置前。
   - 在 `showEvent` 中延迟重复应用，避免窗口重建后失效。

3. **不影响其他软件操作**
   - 窗口不抢焦点，用户点击其他窗口时焦点会正常切换。
   - 点击检测仅对“实体像素”生效：`mousePressEvent` 内部通过图片 alpha 进行命中测试，
     透明区域 `event.ignore()`，减少对下层窗口的阻挡感。

4. **后台输入监听**
   - `InputMonitor` 使用 `pynput` 全局监听键鼠，让动画不依赖窗口焦点。
   - macOS 需要在“隐私与安全性”中启用 **输入监控** 和 **辅助功能** 权限。

## 数据存储 (Data Persistence)
- **文件**: `save_data.json`
- **内容**: 经验、境界、灵石、背包、市场数据、三维属性、天赋数据。
- **机制**: 程序关闭时自动保存，启动时读取；支持离线收益结算。

## 关键修复 (Critical Fixes)
- 修复了 `PetWindow` 初始化顺序导致的 `image_label` 属性丢失崩溃问题。
- 修复了 macOS 下窗口置顶与焦点抢占的冲突 (使用 `WindowDoesNotAcceptFocus`)。

## 下一步计划 (Next Steps)
- 详见 `plan2.md`
