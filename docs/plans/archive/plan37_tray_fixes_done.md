# Plan 37: 修复托盘菜单状态同步与置顶功能问题

## 1. 问题描述
用户反馈了两个与托盘菜单相关的问题：
1.  **对话显示状态不一致**: 托盘菜单中“显示对话”默认是勾选状态，但程序启动时并未显示对话框。
2.  **置顶功能失效**: 无论“始终置顶”选项是否勾选，窗口似乎一直保持置顶状态，无法取消。

## 2. 目标
- 修正“显示对话”的初始状态，使其与实际 UI 表现一致（默认隐藏或默认显示并勾选）。
- 修复“始终置顶”功能的逻辑，确保用户可以自由切换窗口置顶状态。

## 3. 分析与解决方案

### 3.1 对话显示状态不一致
- **原因推测**: `SystemTray` 初始化时可能强行设置了 `Action` 为 `checked=True`，而 `PetWindow` 初始化时默认隐藏了对话气泡 (`speech_label`)。
- **修复方案**:
    - 检查 `PetWindow` 中对话气泡的初始可见性。
    - 在 `SystemTray` 初始化时，读取 `PetWindow` 的实际状态来设置 `CheckState`，或者统一设定为默认开启并确保 UI 同步显示。

### 3.2 置顶功能失效
- **原因推测**:
    - PyQt 中修改 `WindowStaysOnTopHint` 后如果不调用 `show()`，标志可能不会立即生效。
    - 或者在 `PetWindow` 的 `paintEvent` 或其他更新逻辑中，有代码不断重置窗口标志。
    - 也有可能是 `FramelessWindowHint` 与 `WindowStaysOnTopHint` 在某些 OS 版本下的兼容性问题，需要特定的设置顺序。
- **修复方案**:
    - 审查 `PetWindow.set_always_on_top` 方法。
    - 确保在切换标志后调用 `self.show()` 来刷新窗口状态。
    - 检查是否有其他地方（如拖拽逻辑）复写了窗口 Flags。

## 4. 执行步骤

1.  **代码审查**:
    - 读取 `src/tray_icon.py` 查看菜单初始化逻辑。
    - 读取 `src/pet_window.py` 查看 `toggle_dialog`, `set_always_on_top` 及窗口初始化逻辑。

2.  **修复逻辑**:
    - **Step 2.1**: 修改 `SystemTray` 初始化，确保 `show_dialog_action` 的初始勾选状态与 `pet_window.speech_label` 的可见性一致。
    - **Step 2.2**: 重构 `PetWindow` 的置顶切换逻辑。
        ```python
        def set_always_on_top(self, enabled: bool):
            flags = self.windowFlags()
            if enabled:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.setWindowFlags(flags)
            self.show() # 必须调用以刷新 Flag
        ```

3.  **验证**:
    - 模拟运行环境（虽然无法直接看 GUI，需依赖代码逻辑正确性），检查逻辑闭环。

## 5. 预期结果
- 启动时，托盘菜单的“显示对话”勾选状态如实反映当前是否显示对话。
- 点击“始终置顶”能正确切换窗口层级。

## 5. 执行结果 (Execution Result)
- **显示对话状态同步**: 修复了 `tray_icon.py` 中菜单初始化的逻辑，现在会读取 `PetWindow.notifications_enabled` 的真实状态来设置勾选框。同时在 `PetWindow` 初始化时明确了默认值为 `True`。
- **macOS 置顶修复**: 在 `PetWindow._apply_macos_window_settings` 中增加了逻辑判断，仅当 Qt 窗口标记包含 `WindowStaysOnTopHint` 时才设置 macOS 的 `kCGFloatingWindowLevelKey` (层级 5)，否则设置为普通层级 (层级 0)。
- **验证**: 代码逻辑已修正，符合预期行为。
