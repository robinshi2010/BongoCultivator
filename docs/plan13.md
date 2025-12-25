# Plan 13: 图像透明化处理 (Image Transparency Processing)

## 1. 目标 (Goal)
对生成的视觉素材进行批量处理，将纯白色背景 (#FFFFFF) 替换为透明背景 (Alpha=0)。
**关键要求**: 
1.  仅处理**外部背景**，保留人物主体和衣服内部的白色。
2.  使用泛洪填充 (Flood Fill) 算法，从图片四角开始识别背景，确保不会误伤主体内部的白色像素。
3.  添加一定的容差 (Tolerance)，以处理压缩或抗锯齿可能带来的边缘非纯白问题。

## 2. 待处理图片清单 (Target Assets)
覆盖 `assets/` 目录下最新的所有状态图片：

| 图片名 | 说明 |
| :--- | :--- |
| **炼丹系** | `cultivator_alchemy_low.png`, `cultivator_alchemy_mid.png`, `cultivator_alchemy_high.png` |
| **基础系** | `cultivator_idle.png`, `cultivator_walk.png`, `cultivator_read.png`, `cultivator_drag.png` |
| **战斗系** | `cultivator_cast.png` |
| **渡劫系** | `tribulation_0_foundation.png`, `tribulation_1_goldcore.png`, `tribulation_2_nascentsoul.png` |

## 3. 实现方案 (Implementation Plan)
编写一个 Python 脚本 `tools/process_images.py` 来自动执行此任务。

### 核心逻辑
1.  **加载图片**: 使用 `PIL` (Pillow) 库。
2.  **转为 RGBA**: 确保图片支持 Alpha 通道。
3.  **种子填充 (Seed Fill)**: 
    - 使用 `ImageDraw.floodfill` 或 `skimage` (如果安装了)，或者自定义 BFS/DFS 算法。
    - 考虑到 Pillow 的 `floodfill` 通常填充颜色，我们可以先创建一个 mask。
    - **更稳健的方法**: 
        - 从 (0,0), (w-1, 0), (0, h-1), (w-1, h-1) 四个角开始进行 BFS 搜索。
        - 搜索条件: 像素颜色接近纯白 (RGB > 240, 240, 240)。
        - 将搜索到的像素 Alpha 设为 0。
4.  **边缘平滑 (可选)**: 如果去底后边缘有白边，可进行轻微的腐蚀处理或边缘 Alpha 衰减，但对于像素风格 (Pixel Art) 来说，硬边缘通常更好。
5.  **批量处理**: 遍历清单中的文件，覆盖保存或保存为 `_processed.png` 并重命名。

## 4. 执行步骤 (Execution Steps)
- [ ] 创建 `tools/process_images.py` 脚本。
- [ ] 备份 `assets/` 目录 (以防万一)。
- [x] 运行脚本处理所有指定图片 (已完成)。
- [ ] 手动检视处理结果，确保人物内部没有变透明 (待验证)。

## 5. 渡劫视觉效果实现 (Tribulation Visual Implementation)
**目标**: 
当玩家触发“渡劫/境界突破”事件时（无论是通过满经验+丹药，还是输入 Cheat Code），将宠物状态切换为专属的渡劫状态，并显示对应的特效图片。

### 涉及图片 (Tribulation Assets)
- Lv0 → Lv1 (筑基): `tribulation_0_foundation.png`
- Lv1 → Lv2 (金丹): `tribulation_1_goldcore.png`
- Lv2 → Lv3 (元婴): `tribulation_2_nascentsoul.png`
*后续境界依次类推...*

### 实现逻辑 (Logic Flow)
1.  **Cultivator (Model)**:
    - 在 `attempt_breakthrough` 成功前，或者开始渡劫时，需要通知 UI 进入 `ASCEND` (或新增 `TRIBULATION`) 状态。
    - 鉴于渡劫通常是一个瞬间或短时过程，我们可以设计为：如果不立刻成功，而是播放一段动画。
    - 也可以简单处理：在 `attempt_breakthrough` 方法中，如果判定成功，先返回一个特殊状态标识或 Event，UI 捕获后播放 3-5秒 动画，然后再弹窗提示成功。

2.  **PetWindow (View)**:
    - **资源加载**: 加载 `assets/tribulation_*.png` 系列图片。
    - **状态切换**: 修改 `set_state(PetState.ASCEND)`，使其能根据当前 `layer_index` 动态选择对应的渡劫图片（类似于炼丹的逻辑）。
        - Lv0 -> Show `tribulation_0`
        - Lv1 -> Show `tribulation_1`
        - ...
    - **特效触发**: 在 `EffectWidget` 中添加 `tribulation` 模式的粒子特效（雷电、金光）。

3.  **触发点 (Triggers)**:
    - **正常渡劫**: `Cultivator.attempt_breakthrough()`
    - **秘籍作弊**: `process_secret_command()` 中，如果指令导致境界提升，也应短暂调用渡劫动画。

### 执行步骤
1.  **更新 `PetWindow.load_assets`**: 批量加载 `tribulation_X.png`。
2.  **更新 `PetWindow.set_state`**: 增加 `ASCEND` 状态下根据等级选图的逻辑。
3.  **优化 `Cultivator.attempt_breakthrough`**: 增加回调或异步机制，允许 UI 播放动画。
    - *方案*: 点击“未满/强行”不触发；点击“尝试突破”后，UI 先设为 `ASCEND` 状态，延迟 3秒 后再显示结果弹窗。
4.  **优化 `process_secret_command`**: 在作弊成功后，强制播放 3秒 渡劫动画。
