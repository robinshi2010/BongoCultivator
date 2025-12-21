import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject

class SystemTray(QObject):
    def __init__(self, pet_window, app):
        super().__init__()
        self.pet_window = pet_window
        self.app = app
        
        # 创建托盘图标 (暂时用 idle 图片)
        self.tray_icon = QSystemTrayIcon(self)
        # 尝试获取图标，如果没有就暂时为空
        # loading logic mirrors PetWindow
        if hasattr(pet_window, 'state_images') and len(pet_window.state_images) > 0:
             # Use the first available image
             pixmap = list(pet_window.state_images.values())[0]
             self.tray_icon.setIcon(QIcon(pixmap))
        else:
             self.tray_icon.setIcon(QIcon("assets/icon.png")) # Fallback
             
        self.init_menu()
        self.tray_icon.show()
        
    def init_menu(self):
        menu = QMenu()
        
        # 还原位置 (防止飞出屏幕)
        reset_pos_action = QAction("重置位置", self)
        reset_pos_action.triggered.connect(self.pet_window.reset_position)
        menu.addAction(reset_pos_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
