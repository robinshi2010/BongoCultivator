from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QAction

class InventoryWindow(QWidget):
    def __init__(self, cultivator, parent=None):
        super().__init__(parent) # parent 设为 None 以便独立作为 Tool 窗口，或者设为 parent 但作为 Tool
        
        # 关键：如果有 parent，默认是子控件，除非设置 Window 标志
        # 这里为了灵活定位，我们设为 Tool Window
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.cultivator = cultivator
        self.resize(260, 350)
        
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15) # 留出绘制边框的边距
        
        # 顶部：灵石显示
        self.money_label = QLabel(f"灵石: {self.cultivator.money}")
        self.money_label.setStyleSheet("color: #FFD700; font-size: 14px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.money_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.money_label)
        
        # 中部：物品列表 (自定义样式)
        self.item_list = QListWidget()
        self.item_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 50);
                border: 1px solid rgba(255, 215, 0, 50);
                border-radius: 4px;
                color: white;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid rgba(255, 255, 255, 20);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 215, 0, 40);
                color: #FFD700;
            }
        """)
        self.refresh_list()
        self.item_list.itemClicked.connect(self.show_item_detail)
        main_layout.addWidget(self.item_list)
        
        # 底部：详情与操作
        self.detail_label = QLabel("选择物品...")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #DDD; font-size: 12px; padding: 5px; min-height: 40px;")
        main_layout.addWidget(self.detail_label)
        
        btn_layout = QHBoxLayout()
        
        self.use_btn = QPushButton("使用")
        self.use_btn.setEnabled(False)
        self.use_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 215, 0, 20);
                border: 1px solid #FFD700;
                color: #FFD700;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 60);
            }
            QPushButton:disabled {
                border-color: #666;
                color: #666;
                background-color: transparent;
            }
        """)
        self.use_btn.clicked.connect(self.use_item)
        
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #AAA;
                color: #AAA;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                border-color: white;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.hide)
        
        btn_layout.addWidget(self.use_btn)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制半透明背景
        bg_color = QColor(30, 30, 35, 230) # 深色背景
        border_color = QColor(255, 215, 0, 180) # 金色边框
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(rect, 10, 10)

    def refresh_list(self):
        self.item_list.clear()
        for name, count in self.cultivator.inventory.items():
            if count > 0:
                self.item_list.addItem(f"{name} x{count}")

    def show_item_detail(self, item):
        item_text = item.text()
        name = item_text.split(" x")[0]
        self.current_selected_item = name
        
        info = self.cultivator.ITEMS.get(name, {})
        desc = info.get("desc", "未知物品")
        self.detail_label.setText(f"【{name}】\n{desc}")
        
        self.use_btn.setEnabled(True)

    def use_item(self):
        if not hasattr(self, 'current_selected_item'):
            return
            
        name = self.current_selected_item
        if self.cultivator.inventory.get(name, 0) <= 0:
            return

        # 使用逻辑
        info = self.cultivator.ITEMS.get(name, {})
        item_type = info.get("type", "misc")
        
        msg = ""
        used_success = False
        
        if item_type == "exp":
            val = info.get("value", 0)
            self.cultivator.gain_exp(val)
            msg = f"使用了 {name}, 修为增加 {val}!"
            used_success = True
        elif item_type == "material" or item_type == "breakthrough":
             # 暂时没有用途，但允许消耗掉
            msg = "使用了该物品，感觉神清气爽 (功能开发中)"
            used_success = True
        else:
            msg = "无法使用"

        if used_success:
            self.cultivator.inventory[name] -= 1
            # 通知 label
            self.detail_label.setText(msg)
            # 刷新
            self.refresh_list()
            self.money_label.setText(f"灵石: {self.cultivator.money}")
            
            # 如果数量归零，清空选择
            if self.cultivator.inventory[name] <= 0:
                self.detail_label.setText("物品已用完")
                self.use_btn.setEnabled(False)
