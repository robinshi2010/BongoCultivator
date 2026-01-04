import sys
import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject
from src.utils.path_helper import get_resource_path

class SystemTray(QObject):
    def __init__(self, pet_window, app):
        super().__init__()
        self.pet_window = pet_window
        self.app = app
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 1. 优先尝试加载专用托盘图标
        tray_icon_path = get_resource_path("assets/tray_icon.png")
        if os.path.exists(tray_icon_path):
             self.tray_icon.setIcon(QIcon(tray_icon_path))
        # 2. 其次尝试使用 PetWindow 的状态图 (角色图)
        elif hasattr(pet_window, 'state_images') and len(pet_window.state_images) > 0:
             # Use the first available image
             pixmap = list(pet_window.state_images.values())[0]
             self.tray_icon.setIcon(QIcon(pixmap))
        # 3. 最后回退到默认图标
        else:
             fallback_path = get_resource_path("assets/icon.png")
             self.tray_icon.setIcon(QIcon(fallback_path))
             
        self.init_menu()
        self.tray_icon.show()
        
    def init_menu(self):
        menu = QMenu()
        
        # 还原位置 (防止飞出屏幕)
        reset_pos_action = QAction("重置位置", self)
        reset_pos_action.triggered.connect(self.pet_window.reset_position)
        menu.addAction(reset_pos_action)
        
        # 始终置顶
        self.top_action = QAction("始终置顶", self)
        self.top_action.setCheckable(True)
        self.top_action.setChecked(True)
        self.top_action.triggered.connect(self.pet_window.set_always_on_top)
        menu.addAction(self.top_action)

        # 显示气泡/对话
        self.notify_action = QAction("显示对话", self)
        self.notify_action.setCheckable(True)
        # Apply initial state from PetWindow
        if hasattr(self.pet_window, 'notifications_enabled'):
            self.notify_action.setChecked(self.pet_window.notifications_enabled)
        else:
            self.notify_action.setChecked(True)
        self.notify_action.triggered.connect(self.pet_window.toggle_notifications)
        menu.addAction(self.notify_action)

        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    def set_tooltip(self, text):
        self.tray_icon.setToolTip(text)
