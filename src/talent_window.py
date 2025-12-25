from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class TalentWindow(QWidget):
    def __init__(self, cultivator, parent=None):
        super().__init__(parent)
        self.cultivator = cultivator
        
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(300, 400)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("【凝神内视】")
        title.setStyleSheet("color: #FFD700; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 基础属性区域
        stat_frame = QFrame()
        stat_frame.setStyleSheet("background-color: rgba(255, 255, 255, 10); border-radius: 5px;")
        stat_layout = QVBoxLayout(stat_frame)
        
        # 境界显示
        self.layer_label = QLabel()
        self.layer_label.setStyleSheet("color: #FFAA00; font-size: 16px; font-weight: bold;")
        stat_layout.addWidget(self.layer_label)

        # 经验条
        from PyQt6.QtWidgets import QProgressBar
        self.exp_bar = QProgressBar()
        self.exp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                color: white;
                background-color: #222;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: #00AAFF;
            }
        """)
        self.exp_bar.setFormat("%v / %m")
        stat_layout.addWidget(self.exp_bar)

        self.mind_label = QLabel()
        self.body_label = QLabel()
        self.aff_label = QLabel() 
        self.death_label = QLabel()
        
        for lbl in [self.mind_label, self.body_label, self.aff_label, self.death_label]:
            lbl.setStyleSheet("color: white; font-size: 14px;")
            stat_layout.addWidget(lbl)
            
        layout.addWidget(stat_frame)
        
        layout.addSpacing(10)
        
        # 天赋点数
        self.points_label = QLabel()
        self.points_label.setStyleSheet("color: #00FF7F; font-size: 16px; font-weight: bold;")
        self.points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.points_label)

# ... inside refresh_data ...

        self.mind_label.setText(f"心魔: {self.cultivator.mind} / 100")
        self.body_label.setText(f"体魄: {self.cultivator.body}")
        self.aff_label.setText(f"气运: {self.cultivator.affection}")
        self.death_label.setText(f"轮回: {self.cultivator.death_count} 世")
        
        # 刷新点数
        pts = self.cultivator.talent_points
        legacy = getattr(self.cultivator, 'legacy_points', 0)
        self.points_label.setText(f"剩余天赋点: {pts}\n(先天传承: {legacy})")
        
        # 天赋加点区域
        talent_frame = QFrame()
        talent_frame.setStyleSheet("background-color: rgba(0, 0, 0, 40); border-radius: 5px;")
        talent_layout = QVBoxLayout(talent_frame)
        
        # 1. 经验天赋
        self.exp_talent_widget = self.create_talent_row("悟性 (经验+5%)", "exp")
        talent_layout.addLayout(self.exp_talent_widget)
        
        # 2. 掉落天赋
        self.drop_talent_widget = self.create_talent_row("福源 (掉率+5%)", "drop")
        talent_layout.addLayout(self.drop_talent_widget)
        
        layout.addWidget(talent_frame)
        
        layout.addStretch()
        
        close_btn = QPushButton("灵识归位")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #AAA;
                color: #AAA;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                border-color: white;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # 定时刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(500) # 0.5s 刷新
        
    def create_talent_row(self, name, talent_key):
        row = QHBoxLayout()
        
        label = QLabel(name)
        label.setStyleSheet("color: #DDD; font-size: 14px;")
        
        val_label = QLabel("Lv.0")
        val_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        val_label.setObjectName("val_label") # for finding later if needed, but we use closure
        
        btn = QPushButton("+")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 127, 20);
                border: 1px solid #00FF7F;
                color: #00FF7F;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 127, 60);
            }
            QPushButton:disabled {
                border-color: #555;
                color: #555;
                background-color: transparent;
            }
        """)
        
        # 使用闭包绑定
        btn.clicked.connect(lambda: self.on_add_talent(talent_key))
        
        row.addWidget(label)
        row.addStretch()
        row.addWidget(val_label)
        row.addWidget(btn)
        
        # Store references in the layout object (hacky but works) or a wrapper
        # Let's verify updating method: refresh_data will iterate layouts or we store widgets in a dict
        if not hasattr(self, 'talent_widgets'):
            self.talent_widgets = {}
        self.talent_widgets[talent_key] = {
            "val_label": val_label,
            "btn": btn
        }
        
        return row
        
    def on_add_talent(self, key):
        if self.cultivator.upgrade_talent(key):
            self.refresh_data()
            
    def refresh_data(self):
        # 刷新基础属性
        self.layer_label.setText(f"当前境界: {self.cultivator.current_layer} ({self.cultivator.layer_index}重)")
        
        self.exp_bar.setMaximum(self.cultivator.max_exp)
        self.exp_bar.setValue(self.cultivator.exp)
        self.exp_bar.setFormat(f"修为: %v / %m")
        
        self.mind_label.setText(f"心魔: {self.cultivator.mind} / 100")
        self.body_label.setText(f"体魄: {self.cultivator.body}")
        self.aff_label.setText(f"气运: {self.cultivator.affection}")
        
        # 刷新点数
        pts = self.cultivator.talent_points
        self.points_label.setText(f"剩余天赋点: {pts}")
        
        # 刷新天赋行
        for key, widgets in self.talent_widgets.items():
            level = self.cultivator.talents.get(key, 0)
            widgets["val_label"].setText(f"Lv.{level}")
            widgets["btn"].setEnabled(pts > 0)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        bg_color = QColor(20, 20, 25, 240)
        border_color = QColor(100, 100, 100, 150)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, 8, 8)
