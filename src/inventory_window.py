from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QGraphicsDropShadowEffect, QListWidgetItem, QTextEdit
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QAction
from src.logger import logger

from src.ui.base_window import DraggableWindow

class InventoryWindow(DraggableWindow):
    def __init__(self, cultivator, pet_window=None, parent=None):
        super().__init__(parent)
        self.pet_window = pet_window
        
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.cultivator = cultivator
        self.item_manager = cultivator.item_manager
        self.resize(260, 350)
        
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部：灵石显示
        self.money_label = QLabel(f"灵石: {self.cultivator.money}")
        self.money_label.setStyleSheet("color: #FFD700; font-size: 14px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.money_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.money_label)
        
        # 中部：物品列表
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
        # 底部：详情与操作
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("background-color: transparent; border: none; color: #DDD;")
        # Fix height to allow scroll
        self.detail_text.setFixedHeight(100)
        main_layout.addWidget(self.detail_text)
        
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
        # cultivator.inventory store keys as item_id now
        for item_id, count in self.cultivator.inventory.items():
            if count > 0:
                item_data = self.item_manager.get_item(item_id)
                if item_data:
                    name = item_data["name"]
                else:
                    # Fallback translation for legacy items
                    name = self.translate_legacy_id(item_id)
                
                list_item = QListWidgetItem(f"{name} x{count}")
                list_item.setData(Qt.ItemDataRole.UserRole, item_id) # Store ID
                self.item_list.addItem(list_item)
                
        self.money_label.setText(f"灵石: {self.cultivator.money}")

    def show_item_detail(self, item):
        item_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_selected_id = item_id
        
        info = self.item_manager.get_item(item_id)
        if not info:
            return
            
        # New HTML display
        html = self.item_manager.get_item_details_html(item_id)
        self.detail_text.setHtml(html)
        
        item_type = info.get("type", "misc")
        
        # 允许使用的类型扩展
        allowed_types = [
            "consumable", "breakthrough", "break", 
            "buff", "exp", "stat", "recov", "utility", "special", "cosmetic"
        ]
        can_use = item_type in allowed_types
        self.use_btn.setEnabled(can_use)

    def use_item(self):
        if not hasattr(self, 'current_selected_id'):
            return
            
        item_id = self.current_selected_id
        if self.cultivator.inventory.get(item_id, 0) <= 0:
            return

        info = self.item_manager.get_item(item_id)
        if not info: return
        
        item_type = info.get("type", "misc")
        effects = info.get("effect", {})
        
        msg = ""
        used_success = False
        
        # Breakthrough Logic (Mapped from 'break' or 'breakthrough')
        if item_type in ["breakthrough", "break"]:
             # Prefer 'breakthrough_chance' (new) over 'chance' (old)
             chance_percent = effects.get("breakthrough_chance", effects.get("chance", 0))
             
             # If chance is like 0.2 (20%), handle it. If > 1 (20), handle it.
             if chance_percent > 1.0:
                 base_rate = chance_percent / 100.0
             else:
                 base_rate = chance_percent
             
             success, res_msg = self.cultivator.attempt_breakthrough(base_rate)
             msg = res_msg
             
             if not success and "修为" in res_msg:
                 msg = res_msg
                 used_success = False # 不扣物品
             else:
                 used_success = True # 尝试了，扣物品

        # Consumable Logic (All other types)
        else:
            # 1. EXP
            if "exp" in effects:
                val = effects["exp"]
                self.cultivator.gain_exp(val)
                msg = f"服用了 {info['name']}, 修为增加 {val}!"
                used_success = True
            elif "exp_gain" in effects:
                val = effects["exp_gain"]
                # If < 1.0, treat as percentage of max_exp
                if val < 1.0:
                    amount = int(self.cultivator.max_exp * val)
                else:
                    amount = int(val)
                self.cultivator.gain_exp(amount)
                msg = f"服用了 {info['name']}, 修为精进 {amount}!"
                used_success = True

            # 2. Stat
            elif "stat_body" in effects:
                val = effects["stat_body"]
                self.cultivator.modify_stat("body", val)
                msg = f"体魄增加了 {val} 点 (永久)"
                used_success = True
            
            # 3. Heal/Recover
            elif "heal" in effects:
                val = effects["heal"]
                msg = f"恢复了 {val} 点状态 (暂无实效)"
                used_success = True
            elif "mind_heal" in effects:
                val = effects["mind_heal"]
                self.cultivator.modify_stat("mind", -val)
                msg = f"心魔减少了 {val} 点"
                used_success = True
            
            # 4. Buffs
            elif "buff" in effects:
                buff_name = effects["buff"]
                duration = effects.get("duration", 0)
                msg = f"获得了增益 [{buff_name}] 持续 {duration//60} 分钟 (开发中)"
                used_success = True
                
            # 5. Affection
            elif "affection" in effects:
                val = effects["affection"]
                self.cultivator.modify_stat("affection", val)
                msg = f"宠物好感度增加 {val} 点"
                used_success = True
                
            # 6. Special Actions
            elif "action" in effects:
                action = effects["action"]
                if action == "reset_talent":
                    self.cultivator.modify_stat("reset_talent", 0)
                    msg = "已洗髓伐骨，天赋点已重置！"
                    used_success = True
            
            # 9. Fallback Logic for items with NO specific effect keys but valid types
            if not used_success:
                if item_type == "recov":
                     val = 10
                     self.cultivator.modify_stat("mind", -val)
                     msg_parts.append(f"心魔-{val}(基础)")
                     used_success = True
                elif item_type == "stat":
                     val = 1
                     self.cultivator.modify_stat("body", val)
                     msg_parts.append(f"体魄+{val}(基础)")
                     used_success = True

            if used_success:
                msg = f"服用了 {info['name']}: " + ", ".join(msg_parts)
            else:
                msg = "物品已使用，但好像没发生什么。"
                used_success = True # Consume it anyway? Or prevent?
                
        if used_success:
            self.cultivator.inventory[item_id] -= 1
            logger.info(f"使用了物品: {info['name']}")
            
            # Optional: update detail text to show used feedback if needed, 
            # but usually we just keep the item description.
            # self.detail_text.setHtml(msg) # Maybe not needed clutter
            if self.pet_window:
                self.pet_window.show_notification(msg)
            self.refresh_list()
            
            if self.cultivator.inventory[item_id] <= 0:
                self.detail_text.setHtml("<b>物品已用完</b>")
                self.use_btn.setEnabled(False)

    def translate_legacy_id(self, item_id):
        # 简单映射常见旧物品ID
        legacy_map = {
            "ore_copper": "铜矿石",
            "ore_ice": "寒冰矿",
            "water_rootless": "无根水",
            "milk_earth": "地心乳",
            "ice_century": "万年冰",
            "herb_sun": "烈阳草",
            "core_beast_2": "二阶兽丹",
            "herb_foundation": "筑基草",
            "flower_purple": "紫猴花",
            "incense_lure": "引妖香",
            "meat_beast": "妖兽肉",
            "bamboo_thunder": "天雷竹",
            "skin_snake": "蛇皮",
            "date_fire": "火枣",
            "herb_illusion": "幻心草",
            "pill_peiyuan": "培元丹",
            "pill_zhenyuan": "真元丹",
            "pill_turtle": "龟息丹",
            "pill_eye": "明目丹"
        }
        return legacy_map.get(item_id, item_id)
