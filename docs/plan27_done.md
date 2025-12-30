# Plan 27: 统一窗口拖拽功能 (Unified Draggable Windows)

## 问题描述 (Problem)
目前只有“修仙记录”（StatsWindow? 或 PetWindow）支持拖拽，其他如坊市、背包等窗口无法拖拽，体验不割裂。用户希望所有通过右键菜单打开的子窗口都具备统一的拖拽能力。

## 目标 (Goals)
1.  **统一体验**: 所有子窗口（Inventory, Market, Alchemy, Stats, Talent）都支持鼠标左键按住拖拽。
2.  **代码复用**: 避免在每个 Window 类中重复写 `mousePressEvent` / `mouseMoveEvent`。

## 实施步骤 (Implementation Steps)

### 步骤 1: 创建基类 (`src/ui/base_window.py`)
定义一个 `DraggableWindow` 基类，继承自 `QWidget` (或 `QMainWindow`)。
在该类中实现标准的拖拽逻辑：

```python
class DraggableWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dragging = False
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
```

### 步骤 2: 重构现有窗口
修改以下文件，使其继承自 `DraggableWindow` 而不是普通的 `QWidget`：
*   `src/inventory_window.py` (`InventoryWindow`)
*   `src/market_window.py` (`MarketWindow`)
*   `src/alchemy_window.py` (`AlchemyWindow`)
*   `src/ui/stats_window.py` (`StatsWindow`)
*   `src/talent_window.py` (`TalentWindow`)

### 步骤 3: 检查冲突
*   确认这些窗口内部是否有控件（如 TableView, ScrollArea）占满了整个区域导致鼠标事件被吞。
*   如果有，可能需要让“标题栏”或“背景区”专门负责拖拽，或者使用 `windowHandle().startSystemMove()` (PyQt6高级特性，视平台支持而定)。
*   对于无边框窗口 (`FramelessWindowHint`)，上述手动计算 `move` 的方法是最通用的。

### 步骤 4: 验证
打开各个窗口，尝试拖拽，确保平滑且不卡顿。

## 执行记录 (Execution Log)
- **2025-12-30**:
    - **基类**: 创建了 `src/ui/base_window.py` 和 `DraggableWindow` 类。
    - **重构**: 
        - `InventoryWindow`, `MarketWindow`, `AlchemyWindow`, `TalentWindow` 已继承自 `DraggableWindow`。
        - `StatsWindow` 继承自 `DraggableWindow` 并删除了其内部原有的冗余拖拽代码。
    - **结果**: 所有子窗口现在都可以通过按住非交互区域（如标题栏、背景）进行拖拽。
    - 任务完成。
