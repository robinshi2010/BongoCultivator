import sys
import os
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QPixmap, QAction, QMouseEvent, QCursor
from src.state import PetState
from src.input_monitor import InputMonitor
from src.cultivator import Cultivator

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 核心数据
        self.cultivator = Cultivator()
        
        # 路径处理
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.save_path = os.path.join(project_root, 'save_data.json')
        
        self.cultivator.load_data(self.save_path)
        
        self.init_ui()
        self.load_assets()
        
        # 拖拽相关
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # 核心逻辑
        self.monitor = InputMonitor()
        self.monitor.start()
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(1000) # 1秒刷新一次

    def game_loop(self):
        apm = self.monitor.get_apm()
        gain_msg, is_combat = self.cultivator.update(apm)
        
        # 检查有没有新的事件需要通知
        if self.cultivator.events:
            # 取出最新的一个事件显示 (防止刷屏)
            latest_event = self.cultivator.events[-1]
            self.show_notification(latest_event)
            self.cultivator.events.clear() # 清空日志，或者你可以保留日志到界面查看
        
        if is_combat:
            if self.current_state != PetState.COMBAT:
                self.set_state(PetState.COMBAT)
        else:
            if self.current_state != PetState.IDLE:
                self.set_state(PetState.IDLE)
                
    def show_notification(self, text):
        # 简单的飘字效果，这里暂时直接用 info_label 显示一会
        # 更好的做法是创建一个独立的 FloatingLabel 类
        self.info_label.setText(text)
        QTimer.singleShot(2000, lambda: self.info_label.setText("准备修仙..."))

    def closeEvent(self, event):
        self.cultivator.save_data(self.save_path)
        self.monitor.stop()
        super().closeEvent(event)

    def init_ui(self):
        # 1. 窗口属性设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # 无边框
            Qt.WindowType.WindowStaysOnTopHint |      # 始终置顶
            Qt.WindowType.Tool                        # 工具窗口
        )
        
        # 2. 核心透明设置 (macOS 关键)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        # 设置整个窗口的样式为透明
        self.setStyleSheet("background: transparent;")
        
        # 3. 初始位置与大小
        self.resize(300, 350)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 350, screen.height() - 400)

        # 4. 图片容器 (用于动画)
        self.image_container = QWidget(self)
        self.image_container.resize(200, 200)
        self.image_container.move(50, 60) # 初始位置
        
        self.image_label = QLabel(self.image_container)
        self.image_label.setScaledContents(True)
        self.image_label.resize(200, 200)
        self.image_label.move(0, 0) # 相对 container 0,0
        
        # 5. 信息 Label (默认精简，无背景)
        self.info_label = QLabel(self)
        self.info_label.resize(280, 50)
        self.info_label.move(10, 10) # 顶部
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 使用文字阴影代替黑底，看起来更融合
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                font-weight: 900;
                qproperty-alignment: AlignCenter;
            }
        """)
        # 添加阴影效果 (通过 GraphicsEffect)
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(1, 1)
        self.info_label.setGraphicsEffect(shadow)
        
        self.info_label.setText("准备修仙...")

        # 6. 呼吸/悬浮动画定时器
        self.float_timer = QTimer(self)
        self.float_timer.timeout.connect(self.update_floating_animation)
        self.float_timer.start(50) # 20fps
        
        self.float_y = 0
        self.float_direction = 1
        self.base_y = 60 # 图片的基础 Y 坐标

    def update_floating_animation(self):
        # 简单的上下浮动 (Sin 也可以，这里用简单的增量)
        if self.current_state == PetState.IDLE:
            speed = 0.5
            range_limit = 10
        else:
            speed = 2 # 战斗时浮动更快
            range_limit = 5
            
        self.float_y += speed * self.float_direction
        
        if abs(self.float_y) > range_limit:
            self.float_direction *= -1
            
        self.image_container.move(50, int(self.base_y + self.float_y))

    def paintEvent(self, event):
        # 确保绘制是透明的 (重写 paintEvent 有助于解决某些系统下的黑框)
        pass 
        # 不需要手动绘制背景，依靠 WA_TranslucentBackground + setStyleSheet

    # --- 鼠标悬停交互 ---
    def enterEvent(self, event):
        # 鼠标移入：显示详细信息
        msg, _ = self.cultivator.update(0) # 获取当前状态文本
        self.info_label.setText(f"【{self.cultivator.current_layer}】\n灵石: {self.cultivator.money} | APM: {self.monitor.get_apm_snapshot()}")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 15px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # 鼠标移出：恢复简约显示
        self.info_label.setText(f"{self.cultivator.current_layer}")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 900;
                background-color: transparent;
            }
        """)
        super().leaveEvent(event)

    def load_assets(self):
        # 资源路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        assets_path = os.path.join(project_root, 'assets')
        
        # 预加载所有状态图片
        self.state_images = {}
        
        # IDLE
        idle_path = os.path.join(assets_path, 'cultivator_idle.png')
        if os.path.exists(idle_path):
            self.state_images[PetState.IDLE] = QPixmap(idle_path)
            
        # COMBAT
        combat_path = os.path.join(assets_path, 'cultivator_cast.png')
        if os.path.exists(combat_path):
            self.state_images[PetState.COMBAT] = QPixmap(combat_path)
            
        # 默认显示 IDLE
        if PetState.IDLE in self.state_images:
            self.set_state(PetState.IDLE)
        else:
            self.info_label.setText("资源缺失")

    def set_state(self, state: PetState):
        if hasattr(self, 'state_images') and state in self.state_images:
            self.current_state = state
            self.image_label.setPixmap(self.state_images[state])

    # --- 鼠标拖拽逻辑 ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            event.accept()
            
    # --- 右键菜单 ---
    def show_context_menu(self, pos):
        menu = QMenu(self)
        # 修仙风格暗色菜单
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 44, 52, 240);
                border: 1px solid #FFD700;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                color: #FFFFFF;
                padding: 8px 24px;
                font-family: "Microsoft YaHei";
                font-size: 13px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 215, 0, 40);
                color: #FFD700;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 215, 0, 50);
                margin: 5px 10px;
            }
        """)
        
        status_action = QAction(f'境界: {self.cultivator.current_layer}', self)
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        menu.addSeparator()

        # 打开背包
        bag_action = QAction('储物袋', self)
        bag_action.triggered.connect(self.open_inventory)
        menu.addAction(bag_action)
        
        menu.addSeparator()
        
        quit_action = QAction('归隐山林 (退出)', self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec(pos)

    def open_inventory(self):
        # 延迟导入防止循环依赖
        from src.inventory_window import InventoryWindow
        
        # 单例/缓存处理：如果还没创建过，就创建
        if not hasattr(self, 'inventory_window') or self.inventory_window is None:
            self.inventory_window = InventoryWindow(self.cultivator, None) # parent=None 保证它是独立窗口，不受主窗口裁剪限制
            
        # 计算位置：显示在桌宠右侧或者左侧，防止出屏幕
        pet_geo = self.frameGeometry()
        screen_geo = QApplication.primaryScreen().geometry()
        
        # 默认放右边
        target_x = pet_geo.right() + 10
        target_y = pet_geo.top()
        
        # 如果右边放不下，就放左边
        if target_x + self.inventory_window.width() > screen_geo.right():
            target_x = pet_geo.left() - self.inventory_window.width() - 10
            
        self.inventory_window.move(target_x, target_y)
        self.inventory_window.show()
        self.inventory_window.refresh_list() # 刷新数据

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = PetWindow()
    pet.show()
    sys.exit(app.exec())
