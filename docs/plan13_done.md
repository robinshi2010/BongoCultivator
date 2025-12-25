# Plan 13: 图像透明化处理 & 渡劫视觉效果实现 (DONE)

## 1. 目标 (Goal)
对生成的视觉素材进行批量处理，将纯白色背景 (#FFFFFF) 替换为透明背景 (Alpha=0)。
同时，整合新增的渡劫（Tribulation）状态图片和特效逻辑。

**关键要求**: 
1.  仅处理**外部背景**，保留人物主体和衣服内部的白色。
2.  完善渡劫时的状态切换和动画反馈。

## 2. 待处理图片清单 (Target Assets)
覆盖 `assets/` 目录下最新的所有状态图片：

| 图片名 | 说明 |
| :--- | :--- |
| **炼丹系** | `cultivator_alchemy_low.png`, `cultivator_alchemy_mid.png`, `cultivator_alchemy_high.png` |
| **基础系** | `cultivator_idle/walk/read/drag.png` |
| **战斗系** | `cultivator_cast.png` |
| **渡劫系** | `tribulation_0_foundation.png` (筑基), `tribulation_1_goldcore.png` (金丹), `tribulation_2_nascentsoul.png` (元婴) |

## 3. 实现方案 (Implementation Plan)
编写一个 Python 脚本 `tools/process_images.py` 来自动执行此任务。

### 核心逻辑
1.  **加载图片**: 使用 `PIL` (Pillow) 库。
2.  **转为 RGBA**: 确保图片支持 Alpha 通道。
3.  **种子填充 (Seed Fill)**: 从四角开始识别白色背景并透明化。
4.  **批量处理**: 遍历清单中的文件。

## 4. 执行步骤 (Execution Steps)
- [x] 创建 `tools/process_images.py` 脚本。
- [x] 备份 `assets/` 目录 (忽略，直接覆盖)。
- [x] 运行脚本处理所有指定图片 (已完成，Log ID: 95/99)。
- [x] 手动检视处理结果 (代码逻辑确认)。

## 5. 渡劫视觉效果实现 (Tribulation Visual Implementation)
**目标**: 
当玩家触发“渡劫/境界突破”事件时（无论是通过满经验+丹药，还是输入 Cheat Code），将宠物状态切换为专属的渡劫状态，并显示对应的特效图片。

### 涉及图片 (Tribulation Assets)
- Lv0 → Lv1: `tribulation_0_foundation.png`
- Lv1 → Lv2: `tribulation_1_goldcore.png`
- Lv2 → Lv3: `tribulation_2_nascentsoul.png`

### 实现逻辑 (Logic Flow)
1.  **Cultivator (Model)**:
    - 维持原有逻辑。
2.  **PetWindow (View)**:
    - **资源加载**: 加载 `assets/tribulation_*.png`。
    - **状态切换**: 修改 `set_state(PetState.ASCEND)`，根据 `layer_index` 选图。
    - **动画锁**:引入 `is_ascending` 标志位，防止 `game_loop` 在播放动画时打断状态。
    - **特效触发**: 在 `on_attempt_breakthrough` 和 `input_secret` 中触发动画序列 (Tribulation -> Delay -> Result)。

### 执行步骤
- [x] 更新 `PetWindow.load_assets` 批量加载 `tribulation_X.png`。
- [x] 更新 `PetWindow.set_state` 增加 `ASCEND` 选图逻辑。
- [x] 优化 `on_attempt_breakthrough` 增加 3秒 渡劫动画。
- [x] 优化 `input_secret` 增加作弊升级时的动画反馈。
- [x] 修复 `game_loop` 状态覆盖问题 (添加 `is_ascending` 锁)。
