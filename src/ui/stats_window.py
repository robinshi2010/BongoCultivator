from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTabWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体 (尝试多个常用中文字体)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Heiti TC', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
# Dark theme for plot
plt.style.use('dark_background')

from src.services.stats_analyzer import stats_analyzer
from src.ui.merit_tab import MeritTab

from src.ui.base_window import DraggableWindow

class StatsWindow(DraggableWindow):
    def __init__(self, cultivator=None, parent=None):
        super().__init__(parent)
        self.cultivator = cultivator
        self.setWindowTitle("修炼记录 - 天道酬勤")
        self.resize(600, 500)
        
        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Frame (Dark Glass)
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 240);
                border: 1px solid #444;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)
        
        self.layout_container = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.container)
        
        # Header (Close Button)
        self.init_header()
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: transparent;
                color: #888;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                color: #FFD700;
                border-bottom: 2px solid #FFD700;
            }
        """)
        self.layout_container.addWidget(self.tabs)
        
        # Tab 1: Today
        self.tab_today = QWidget()
        self.init_tab_today()
        self.tabs.addTab(self.tab_today, "今日修仙")
        
        # Tab 2: History (Placeholder for now)
        self.tab_history = QWidget()
        self.init_tab_history()
        self.tabs.addTab(self.tab_history, "历史长河")
        
        # Tab 3: Merit (Achievements)
        self.tab_merit = MeritTab(self.cultivator)
        self.tabs.addTab(self.tab_merit, "功德簿")
        
        # Auto refresh logic
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        # self.timer.start(60000) # Refresh every minute if open? 
        
    def init_header(self):
        header = QHBoxLayout()
        title = QLabel("📊 修炼数据分析")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border: none;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                color: #AAA; background: transparent; 
                font-size: 20px; border: none; font-weight: bold;
            }
            QPushButton:hover { color: #FFF; }
        """)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        self.layout_container.addLayout(header)

    def init_tab_today(self):
        layout = QVBoxLayout(self.tab_today)
        
        # Summary Row
        summary_layout = QHBoxLayout()
        self.lbl_total_keys = self._create_stat_card("⌨️ 敲击数", "0")
        self.lbl_total_mouse = self._create_stat_card("🖱️ 点击数", "0")
        self.lbl_active_time = self._create_stat_card("⏱️ 专注(分)", "0")
        
        summary_layout.addWidget(self.lbl_total_keys)
        summary_layout.addWidget(self.lbl_total_mouse)
        summary_layout.addWidget(self.lbl_active_time)
        layout.addLayout(summary_layout)
        
        # Chart
        self.figure_today = Figure(figsize=(5, 3), dpi=100)
        self.figure_today.patch.set_facecolor('none') # Transparent
        self.canvas_today = FigureCanvas(self.figure_today)
        self.canvas_today.setStyleSheet("background-color:transparent;")
        layout.addWidget(self.canvas_today)
        
        # Analysis Text
        self.lbl_analysis = QLabel("正在分析天道...")
        self.lbl_analysis.setStyleSheet("color: #AAA; font-size: 12px; margin-top: 5px; border: none;")
        self.lbl_analysis.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_analysis)
        
        # Reward Button
        self.btn_claim = QPushButton("领取今日勤勉赏 (需 >2000 操作)")
        self.btn_claim.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_claim.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 6px; padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.btn_claim.clicked.connect(self.on_claim_clicked)
        layout.addWidget(self.btn_claim)

    def on_claim_clicked(self):
        if not self.cultivator:
             return
             
        # Get latest total actions (keys + clicks)
        try:
             # Assume today_overview is already fetched in refresh_data, or re-fetch
             data = stats_analyzer.get_today_overview()
             total = data['total_keys'] + data['total_mouse']
             
             success, msg = self.cultivator.claim_daily_work_reward(total)
             
             from PyQt6.QtWidgets import QMessageBox
             if success:
                 QMessageBox.information(self, "领取成功", msg)
                 self.btn_claim.setText("今日已领取")
                 self.btn_claim.setEnabled(False)
             else:
                 QMessageBox.warning(self, "无法领取", msg)
                 
        except Exception as e:
             print(f"Error claiming reward: {e}")

    def _create_stat_card(self, title, value):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 10);
                border-radius: 8px;
                border: none;
            }
        """)
        layout = QVBoxLayout(container)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: #FFD700; font-size: 20px; font-weight: bold; border: none; background: transparent;")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        return container

    def update_stat_card(self, widget, value):
        # Helper to find the value label inside the card
        labels = widget.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(str(value))

    def init_tab_history(self):
        layout = QVBoxLayout(self.tab_history)
        
        # 1. Period Selector
        btn_layout = QHBoxLayout()
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 15);
                color: #AAA; border: 1px solid #555; border-radius: 12px;
                padding: 4px 12px; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #FFD700; color: #000; border: 1px solid #FFD700;
            }
        """
        
        self.btn_week = QPushButton("近7天")
        self.btn_week.setCheckable(True)
        self.btn_week.setStyleSheet(btn_style)
        self.btn_week.clicked.connect(lambda: self.switch_history_period('week'))
        
        self.btn_month = QPushButton("本月")
        self.btn_month.setCheckable(True)
        self.btn_month.setStyleSheet(btn_style)
        self.btn_month.clicked.connect(lambda: self.switch_history_period('month'))
        
        self.btn_year = QPushButton("年度")
        self.btn_year.setCheckable(True)
        self.btn_year.setStyleSheet(btn_style)
        self.btn_year.clicked.connect(lambda: self.switch_history_period('year'))
        
        # Group logic manually or use QButtonGroup
        self.history_btns = [self.btn_week, self.btn_month, self.btn_year]
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_week)
        btn_layout.addWidget(self.btn_month)
        btn_layout.addWidget(self.btn_year)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 2. Stats
        stats_layout = QHBoxLayout()
        self.lbl_hist_total = self._create_stat_card("📅 总操作", "0")
        self.lbl_hist_busy = self._create_stat_card("🔥 最忙", "-")
        stats_layout.addWidget(self.lbl_hist_total)
        stats_layout.addWidget(self.lbl_hist_busy)
        layout.addLayout(stats_layout)
        
        # 3. Chart
        self.figure_hist = Figure(figsize=(5, 3), dpi=100)
        self.figure_hist.patch.set_facecolor('none')
        self.canvas_hist = FigureCanvas(self.figure_hist)
        self.canvas_hist.setStyleSheet("background-color:transparent;")
        layout.addWidget(self.canvas_hist)
        
        # Default load
        self.btn_week.setChecked(True)
        self.current_period = 'week'

    def switch_history_period(self, period):
        self.current_period = period
        
        # Update btn states
        for btn in self.history_btns:
            was_checked = (btn.text() == "近7天" and period == 'week') or \
                          (btn.text() == "本月" and period == 'month') or \
                          (btn.text() == "年度" and period == 'year')
            # Simply uncheck others. But since they are independent, we manually manage visual state if needed
            # A simpler way is to just setChecked the target and uncheck others
            if btn.isChecked() and not was_checked:
                btn.setChecked(False)
            if not btn.isChecked() and was_checked:
                btn.setChecked(True)
                
        self.refresh_history()

    def refresh_history(self):
        data = stats_analyzer.get_period_stats(self.current_period)
        
        self.update_stat_card(self.lbl_hist_total, data['total_actions'])
        self.update_stat_card(self.lbl_hist_busy, data['busiest_period'])
        
        self.plot_history_chart(data['trend'], data['labels'])

    def plot_history_chart(self, trend, labels):
        self.figure_hist.clear()
        ax = self.figure_hist.add_subplot(111)
        
        x = range(len(trend))
        # Line chart for history
        ax.plot(x, trend, color='#00FF7F', marker='o', linewidth=2, markersize=4)
        # Fill under
        ax.fill_between(x, trend, color='#00FF7F', alpha=0.1)
        
        # Style
        ax.set_facecolor('none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#666')
        ax.spines['left'].set_color('#666')
        
        ax.tick_params(axis='x', colors='#888')
        ax.tick_params(axis='y', colors='#888')
        
        # Ticks
        # If too many labels, sparse them
        step = 1
        if len(labels) > 10:
            step = len(labels) // 6 + 1
            
        ax.set_xticks(x[::step])
        ax.set_xticklabels(labels[::step])
        
        self.canvas_hist.draw()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
        
    def refresh_data(self):
        # Fetch data
        data = stats_analyzer.get_today_overview()
        
        # Update labels
        self.update_stat_card(self.lbl_total_keys, data['total_keys'])
        self.update_stat_card(self.lbl_total_mouse, data['total_mouse'])
        self.update_stat_card(self.lbl_active_time, data['active_minutes'])
        
        busy = data['most_busy_hour']
        if busy != "-":
            self.lbl_analysis.setText(f"🔥 今日最“卷”时刻: {busy} (修仙强度 MAX)")
        else:
            self.lbl_analysis.setText("🌙 今日尚在摸鱼中...")
            
        # Draw Chart
        self.plot_today_chart(data['hourly_trend'])
        
        # Check Daily Reward Status
        if self.cultivator:
             import datetime
             today_str = datetime.date.today().strftime("%Y-%m-%d")
             if self.cultivator.daily_reward_claimed == today_str:
                 self.btn_claim.setText("今日已领取")
                 self.btn_claim.setEnabled(False)
             else:
                 # New Day or Not Claimed
                 self.btn_claim.setEnabled(True)
                 self.btn_claim.setText("领取今日勤勉赏 (需 >2000 操作)")
        
    def plot_today_chart(self, trend_data):
        self.figure_today.clear()
        ax = self.figure_today.add_subplot(111)
        
        # X Axis: 0-23
        hours = list(range(24))
        
        # Bar chart
        bars = ax.bar(hours, trend_data, color='#FFD700', alpha=0.7)
        
        # Style
        ax.set_facecolor('none') # Transparent chart area
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#666')
        ax.spines['left'].set_color('#666')
        
        ax.tick_params(axis='x', colors='#888')
        ax.tick_params(axis='y', colors='#888')
        
        # Only show some ticks on X to avoid crowding? 
        # For 24h, showing 0, 6, 12, 18, 23 is good
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_xticklabels(['00:00', '06:00', '12:00', '18:00', '23:00'])
        
        self.canvas_today.draw()


