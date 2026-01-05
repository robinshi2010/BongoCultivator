from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, 
                             QHBoxLayout, QListWidgetItem, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from src.state import PetState
from src.logger import logger

from src.ui.base_window import DraggableWindow

class AlchemyWindow(DraggableWindow):
    def __init__(self, cultivator, pet_window, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.cultivator = cultivator
        self.pet_window = pet_window
        self.item_manager = cultivator.item_manager
        self.resize(320, 450)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("【炼丹房】")
        title.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 16px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Recipe List
        self.recipe_list = QListWidget()
        self.style_list_widget(self.recipe_list)
        self.recipe_list.itemClicked.connect(self.show_recipe_detail)
        main_layout.addWidget(self.recipe_list)
        
        # Details Area
        self.detail_label = QLabel("选择丹方...")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #DDD; font-size: 12px; padding: 5px; min-height: 80px;")
        main_layout.addWidget(self.detail_label)
        
        # Progress Bar (for crafting)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #FFD700;
                border-radius: 4px;
                text-align: center;
                background: rgba(0,0,0,50);
                color: white;
            }
            QProgressBar::chunk {
                background-color: #FFD700;
            }
        """)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.craft_btn = QPushButton("开始炼制")
        self.craft_btn.setEnabled(False)
        self.craft_btn.clicked.connect(self.start_crafting)
        self.style_action_btn(self.craft_btn)
        
        close_btn = QPushButton("离开")
        close_btn.clicked.connect(self.hide)
        self.style_normal_btn(close_btn)
        
        btn_layout.addWidget(self.craft_btn)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(40, 20, 20, 240) # Dark Reddish tint for Alchemy
        border_color = QColor(255, 100, 100, 200) # Reddish border
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(rect, 10, 10)

    def refresh_recipes(self):
        self.recipe_list.clear()
        
        tier = min(self.cultivator.layer_index, 8)
        # Show recipes for current tier (and maybe previous?)
        # Let's show current tier only for now to keep list clean
        
        pills = self.item_manager.tier_lists.get(tier, {}).get("pills", [])
        
        for pill_id in pills:
            info = self.item_manager.get_item(pill_id)
            name = info.get("name", pill_id)
            recipe = info.get("recipe", {})
            
            # Skip items without a recipe (cannot be drafted)
            if not recipe:
                continue

            # Check if craftable
            can_craft = self.check_ingredients(recipe)
            
            status_str = " [可炼制]" if can_craft else " [材料不足]"
            color_code = "#00FF00" if can_craft else "#888888"
            
            # Use HTML for color
            # QListWidgetItem doesn't support HTML directly easily unless we use custom widget
            # Let's just append text
            
            item = QListWidgetItem(f"{name}{status_str}")
            item.setData(Qt.ItemDataRole.UserRole, pill_id)
            
            if not can_craft:
                item.setForeground(QBrush(QColor(150, 150, 150)))
            else:
                item.setForeground(QBrush(QColor(255, 215, 0)))
                
            self.recipe_list.addItem(item)
            
    def check_ingredients(self, recipe):
        if not recipe: return False
        for mat_id, count in recipe.items():
            if self.cultivator.inventory.get(mat_id, 0) < count:
                return False
        return True

    def show_recipe_detail(self, item):
        pill_id = item.data(Qt.ItemDataRole.UserRole)
        info = self.item_manager.get_item(pill_id)
        if not info: return
        
        self.current_recipe_id = pill_id
        
        name = info["name"]
        desc = info.get("description", "无描述")
        recipe = info.get("recipe", {})
        
        # Build Ingredients Text
        ing_text = ""
        can_craft = True
        
        for mat_id, req_count in recipe.items():
            mat_info = self.item_manager.get_item(mat_id)
            mat_name = mat_info["name"] if mat_info else mat_id
            has_count = self.cultivator.inventory.get(mat_id, 0)
            
            color = "white" if has_count >= req_count else "red"
            if has_count < req_count: can_craft = False
            
            ing_text += f" - {mat_name}: <font color='{color}'>{has_count}/{req_count}</font><br>"
            
        full_text = f"<b>{name}</b><br>{desc}<br><br>所需材料:<br>{ing_text}"
        self.detail_label.setText(full_text)
        
        self.craft_btn.setEnabled(can_craft)

    def start_crafting(self):
        # Prevent double click
        self.craft_btn.setEnabled(False)
        
        if self.pet_window.is_alchemying:
            logger.warning("炼丹正在进行中，忽略点击")
            return
            
        info = self.item_manager.get_item(self.current_recipe_id)
        recipe = info.get("recipe", {})
        
        logger.info(f"尝试炼丹: {info.get('name')} | 配方: {recipe} |当前库存: {self.cultivator.inventory}")

        # Deduct items
        if self.cultivator.consume_items(recipe):
            logger.info("材料扣除成功，开始炼制")
            # Trigger PetWindow Alchemy State
            self.pet_window.start_alchemy_task(self.current_recipe_id)
            self.hide()
        else:
            logger.warning("材料扣除失败 (不足)")
            self.detail_label.setText("材料不足，无法炼制！")
            self.refresh_recipes() # Refresh to update status

    def showEvent(self, event):
        self.refresh_recipes()
        super().showEvent(event)

    def style_list_widget(self, list_widget):
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 40);
                border: 1px solid rgba(255, 100, 100, 30);
                border-radius: 4px;
                color: #DDD;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid rgba(255, 255, 255, 10);
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: rgba(255, 100, 100, 30);
                color: #FFD700;
            }
        """)

    def style_action_btn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 50, 50, 40);
                border: 1px solid #FFD700;
                color: #FFD700;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background: rgba(200, 50, 50, 80);
            }
            QPushButton:disabled {
                border-color: #666;
                color: #666;
                background: transparent;
            }
        """)

    def style_normal_btn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
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
