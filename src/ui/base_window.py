from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint

class DraggableWindow(QWidget):
    """
    Base class for frameless windows that need to be draggable.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dragging = False
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            # Calculate offset: Global Mouse Pos - Window Top Left
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # We need to check if LeftButton is held down.
        # Note: In mouseMoveEvent, event.buttons() (plural) returns the state of all buttons.
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
