# 修仙桌宠 (Immortal Desk Pet) 开发计划

本项目旨在基于 Python + PyQt6 开发一个桌面宠物应用。核心玩法是通过监听用户的键盘鼠标活动频率（APM）来驱动宠物的修仙行为（打坐、历练、战斗）。

## Phase 1: 基础架构搭建 (Foundation)
- [x] **1.1 环境配置**
    - 创建项目目录结构。
    - 编写 `requirements.txt` (PyQt6, pynput, Pillow)。
    - 创建 `main.py` 入口文件。
- [x] **1.2 透明窗口实现**
    - 实现 `MainWindow` 类。
    - 配置窗口属性：无边框 (Frameless)、背景透明 (Translucent)、始终置顶 (Always on Top)。
    - 解决 macOS 下的透明背景兼容性问题。
- [x] **1.3 基础资源加载**
    - 创建 `assets` 目录。
    - 使用 `generate_image` 生成临时测试用的修仙者占位图（或简单的色块）。
    - 在窗口中显示静态图片。

## Phase 2: 动画与状态机 (Animation & State)
- [x] **2.1 状态机设计 (State Machine)**
    - 定义核心状态枚举：`IDLE` (发呆), `MEDITATE` (打坐/修炼), `WORK` (工作/历练), `COMBAT` (战斗)。
    - 创建 `PetState` 类管理状态切换。
- [x] **2.2 动画系统**
    - 实现 `SpriteAnimator` 类，支持加载序列帧或 GIF。
    - 制作/生成不同状态下的简单帧动画（如：打坐时身体微动，战斗时挥剑）。
    - 将动画系统集成到主窗口，支持 `set_animation(state)`。

## Phase 3: 感知与修仙逻辑 (Core Gameplay)
- [x] **3.1 输入监听 (Input Monitor)**
    - 集成 `pynput` 库。
    - 实现 `InputMonitor` 类，后台统计 Key Press 和 Mouse Move/Click 次数。
    - 实现 APM (Actions Per Minute) 实时计算算法。
    - **注意**: macOS 需要处理辅助功能权限提示。
- [x] **3.2 游戏循环 (Game Loop)**
    - 建立 `QTimer` 定时器作为主逻辑心跳 (比如 1秒 1次)。
    - 根据当前 APM 判定行为：
        - APM < 5: 进入 **打坐模式** (增长修为)。
        - 5 < APM < 100: 进入 **历练模式** (增长灵气/素材)。
        - APM > 100: 进入 **狂暴/战斗模式** (大幅消耗体力，高收益)。
- [x] **3.3 数值系统**
    - 定义 `Cultivator` 类：包含 境界 (Layer), 修为 (Exp), 灵石 (Money)。
    - 实现境界突破逻辑 (练气 -> 筑基 -> 金丹...)。

## Phase 4: 交互与反馈 (Interaction & UI)
- [x] **4.1 视觉反馈**
    - 实现“漂浮文字” (Floating Text) 系统：当获得修为时，头顶飘出 "+1 修为"。
    - 实现右键上下文菜单：查看属性、退出程序。
- [ ] **4.2 属性面板**
    - 创建一个小型的悬浮窗或模态框，显示当前境界、属性详情。
- [x] **4.3 数据持久化**
    - 使用 JSON 保存玩家数据，程序启动时读取。

## Phase 5: 优化与打磨 (Polish)
- [ ] **5.1 交互优化**
    - 支持鼠标拖拽移动桌宠位置。
    - 添加双击交互（摸头）。
- [ ] **5.2 资源替换**
    - (可选) 优化美术资源，生成更好看的修仙像素画。
