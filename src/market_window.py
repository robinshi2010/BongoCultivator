from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, 
                             QHBoxLayout, QTabWidget, QMessageBox, QListWidgetItem, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from src.logger import logger

from src.ui.base_window import DraggableWindow

class MarketWindow(DraggableWindow):
    def __init__(self, cultivator, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.cultivator = cultivator
        self.item_manager = cultivator.item_manager
        self.resize(360, 480) # Widen for details
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部标题 & 灵石
        top_layout = QHBoxLayout()
        title = QLabel("【修仙坊市】")
        title.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 16px;")
        
        self.money_label = QLabel(f"灵石: {self.cultivator.money}")
        self.money_label.setStyleSheet("color: #FFF; font-weight: bold;")
        
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # 刷新按钮 (Moved to top)
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.request_manual_refresh)
        self.btn_refresh.setFixedWidth(50)
        top_layout.addWidget(self.btn_refresh)
        
        top_layout.addWidget(self.money_label)
        main_layout.addLayout(top_layout)
        
        # Timer for button tick
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_refresh_btn)
        self.refresh_timer.start(1000)
        
        # Tab 分页
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: rgba(255, 255, 255, 20);
                color: #AAA;
                padding: 6px 12px;
                border-radius: 4px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 215, 0, 40);
                color: #FFD700;
            }
        """)
        
        self.buy_tab = QWidget()
        self.setup_buy_tab()
        
        self.sell_tab = QWidget()
        self.setup_sell_tab()
        
        self.tabs.addTab(self.buy_tab, "每日特惠")
        self.tabs.addTab(self.sell_tab, "资源回收")
        main_layout.addWidget(self.tabs)
        
        # 底部关闭
        close_btn = QPushButton("离开坊市")
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 10);
                border: 1px solid #666;
                color: #DDD;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
                border-color: #EEE;
            }
        """)
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(20, 20, 25, 240) 
        border_color = QColor(255, 215, 0, 200)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(rect, 10, 10)

    # --- Buy Logic ---
    def setup_buy_tab(self):
        layout = QVBoxLayout(self.buy_tab)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # 提示信息 (Moved to top by user request)
        self.buy_msg = QLabel("每日0点自动刷新 or 点击刷新")
        self.buy_msg.setStyleSheet("color: #888; font-size: 10px;")
        self.buy_msg.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.buy_msg)
        
        self.goods_list = QListWidget()
        self.style_list_widget(self.goods_list)
        self.goods_list.itemClicked.connect(self.show_buy_detail)
        layout.addWidget(self.goods_list)
        
        # Detail View
        self.buy_detail = QTextEdit()
        self.buy_detail.setReadOnly(True)
        self.buy_detail.setStyleSheet("background: transparent; border: none; color: #DDD;")
        self.buy_detail.setFixedHeight(120)
        layout.addWidget(self.buy_detail)
        
        action_layout = QHBoxLayout()
        
        # Buy Button
        self.buy_btn = QPushButton("购买选定")
        self.buy_btn.clicked.connect(self.buy_item)
        self.style_action_btn(self.buy_btn)
        action_layout.addWidget(self.buy_btn) 
        
        layout.addLayout(action_layout)
        
        # Initial status check
        self.update_refresh_btn()

    def update_refresh_btn(self):
        import time
        now = time.time()
        last = self.cultivator.last_market_refresh
        diff = now - last
        
        cooldown = 3600 # 1 hour
        if diff < cooldown:
            remaining = int(cooldown - diff)
            mins = remaining // 60
            secs = remaining % 60
            self.btn_refresh.setText(f"{mins}:{secs:02d}")
            self.btn_refresh.setEnabled(False)
            self.btn_refresh.setStyleSheet("""
                QPushButton {
                    background: rgba(100, 100, 100, 20);
                    border: 1px solid #666;
                    color: #888;
                    border-radius: 4px;
                    padding: 2px;
                    font-size: 10px;
                }
            """)
        else:
            self.btn_refresh.setText("刷新")
            self.btn_refresh.setEnabled(True)
            self.btn_refresh.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 215, 0, 20);
                    border: 1px solid #FFD700;
                    color: #FFD700;
                    border-radius: 4px;
                    padding: 2px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: rgba(255, 215, 0, 50);
                }
            """)

    def request_manual_refresh(self):
        # Double check cd logic handled by cultivator? 
        # Cultivator just does refresh. Logic is usually in UI or check method.
        # Let's enforce it here or updated cultivator.refresh_market to check? 
        # Cultivator.refresh_market just sets time. 
        
        self.cultivator.refresh_market()
        self.refresh_buy_list()
        self.buy_msg.setText("坊市已刷新! 看看有什么好东西?")
        self.update_refresh_btn()

    def refresh_buy_list(self):
        self.goods_list.clear()
        for idx, goods in enumerate(self.cultivator.market_goods):
            item_id = goods["id"]
            price = goods["price"]
            discount = goods["discount"]
            
            info = self.item_manager.get_item(item_id)
            name = info.get("name", "未知") if info else item_id
            
            # 显示折扣与价格
            discount_str = ""
            if discount < 1.0:
                 discount_str = f" [{(discount*10):.1f}折]"
            
            text = f"{name} {discount_str}\n价格: {price} 灵石"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, idx) # Store index in market_goods list
            self.goods_list.addItem(item)
            
        self.update_money()

    def show_buy_detail(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx >= len(self.cultivator.market_goods): return
        
        goods = self.cultivator.market_goods[idx]
        item_id = goods["id"]
        
        html = self.item_manager.get_item_details_html(item_id)
        self.buy_detail.setHtml(html)

    def buy_item(self):
        current_item = self.goods_list.currentItem()
        if not current_item:
            return
            
        idx = current_item.data(Qt.ItemDataRole.UserRole)
        if idx >= len(self.cultivator.market_goods):
            return
            
        goods = self.cultivator.market_goods[idx]
        price = goods["price"]
        item_id = goods["id"]
        
        if self.cultivator.money >= price:
            self.cultivator.money -= price
            self.cultivator.gain_item(item_id, 1)
            
            # 移除商品 (买完就没了)
            self.cultivator.market_goods.pop(idx)
            
            self.buy_msg.setText(f"购买成功! -{price}灵石")
            self.refresh_buy_list()
        else:
            self.buy_msg.setText("灵石不足!")

    # --- Sell Logic ---
    def setup_sell_tab(self):
        layout = QVBoxLayout(self.sell_tab)
        layout.setContentsMargins(0, 10, 0, 0)
        
        self.sell_list = QListWidget()
        self.style_list_widget(self.sell_list)
        self.sell_list.itemClicked.connect(self.show_sell_detail)
        layout.addWidget(self.sell_list)
        
        # Detail View
        self.sell_detail = QTextEdit()
        self.sell_detail.setReadOnly(True)
        self.sell_detail.setStyleSheet("background: transparent; border: none; color: #DDD;")
        self.sell_detail.setFixedHeight(120)
        layout.addWidget(self.sell_detail)
        
        btn_box = QHBoxLayout()
        self.sell_one_btn = QPushButton("出售 1 个")
        self.sell_one_btn.clicked.connect(self.sell_item_one)
        self.style_action_btn(self.sell_one_btn)
        
        self.sell_all_btn = QPushButton("出售整组")
        self.sell_all_btn.clicked.connect(self.sell_item_all)
        self.sell_all_btn.setStyleSheet("""
             QPushButton {
                background: rgba(200, 50, 50, 40);
                border: 1px solid #A55;
                color: #FAA;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background: rgba(200, 50, 50, 80); }
        """)
        
        btn_box.addWidget(self.sell_one_btn)
        btn_box.addWidget(self.sell_all_btn)
        layout.addLayout(btn_box)
        
        self.sell_msg = QLabel("")
        self.sell_msg.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.sell_msg)

    def refresh_sell_list(self):
        current_row = self.sell_list.currentRow()
        current_item = self.sell_list.currentItem()
        selected_item_id = current_item.data(Qt.ItemDataRole.UserRole) if current_item else None

        self.sell_list.clear() # Clears list but we have the ID

        # Sort items? By Tier/Name
        # inventory is dict {id: count}
        # Let's simple list
        
        tier_map = {0: "凡", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}

        restore_item = None

        for item_id, count in self.cultivator.inventory.items():
            if count > 0:
                info = self.item_manager.get_item(item_id)
                name = info.get("name", item_id) if info else item_id
                tier = info.get("tier", 0) if info else 0
                
                base_price = info.get("price", 1) if info else 1
                sell_price = max(1, int(base_price * 0.5))
                
                # Show Tier
                cn_tier = tier_map.get(tier, str(tier))
                tier_str = f"[{cn_tier}{'阶' if tier > 0 else '物'}]"
                
                text = f"{tier_str} {name} x{count}\n售价: {sell_price} 灵石/个"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, item_id)
                self.sell_list.addItem(item)
                
                if selected_item_id and item_id == selected_item_id:
                    restore_item = item
        
        if restore_item:
            self.sell_list.setCurrentItem(restore_item)
            self.sell_list.scrollToItem(restore_item)

        
        self.update_money()

    def show_sell_detail(self, item):
        item_id = item.data(Qt.ItemDataRole.UserRole)
        html = self.item_manager.get_item_details_html(item_id)
        self.sell_detail.setHtml(html)

    def _get_selected_item_info(self):
        current_item = self.sell_list.currentItem()
        if not current_item:
            return None, 0, 0
        item_id = current_item.data(Qt.ItemDataRole.UserRole)
        count = self.cultivator.inventory.get(item_id, 0)
        
        info = self.item_manager.get_item(item_id)
        base_price = info.get("price", 1) if info else 1
        sell_price = max(1, int(base_price * 0.5))
        
        return item_id, count, sell_price

    def sell_item_one(self):
        item_id, count, sell_price = self._get_selected_item_info()
        if not item_id or count <= 0: return

        self.cultivator.inventory[item_id] -= 1
        self.cultivator.money += sell_price
        
        self.sell_msg.setText(f"出售成功! +{sell_price}灵石")
        self.refresh_sell_list()

    def sell_item_all(self):
        item_id, count, sell_price = self._get_selected_item_info()
        if not item_id or count <= 0: return

        total_price = sell_price * count
        self.cultivator.inventory[item_id] = 0
        self.cultivator.money += total_price
        
        self.sell_msg.setText(f"出售 {count}个! 获得 {total_price} 灵石")
        self.refresh_sell_list()

    # --- Utils ---
    def update_money(self):
        self.money_label.setText(f"灵石: {self.cultivator.money}")

    def showEvent(self, event):
        self.refresh_buy_list()
        self.refresh_sell_list()
        super().showEvent(event)

    def style_list_widget(self, list_widget):
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 40);
                border: 1px solid rgba(255, 215, 0, 30);
                border-radius: 4px;
                color: #DDD;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid rgba(255, 255, 255, 10);
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: rgba(255, 215, 0, 30);
                color: #FFD700;
            }
        """)

    def style_action_btn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 215, 0, 20);
                border: 1px solid #FFD700;
                color: #FFD700;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background: rgba(255, 215, 0, 50);
            }
        """)
