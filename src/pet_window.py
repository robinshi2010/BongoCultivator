import sys
import os
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QPixmap, QAction, QMouseEvent, QCursor
from src.state import PetState
from src.input_monitor import InputMonitor
from src.cultivator import Cultivator
from src.logger import logger

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 核心数据
        logger.info("初始化 PetWindow...")
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
        
        # 炼丹状态
        self.is_alchemying = False
        self.alchemy_time = 0
        self.alchemy_target_time = 10
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(1000) # 1秒刷新一次

    def game_loop(self):
        apm = self.monitor.get_apm()
        
        # 如果正在炼丹
        if self.is_alchemying:
            # 高 APM 会打断炼丹
            if apm > 50:
                self.is_alchemying = False
                logger.warning(f"炼丹失败: APM过高 ({apm})")
                self.show_notification("心神不宁，炼丹失败！(APM太高)")
                self.set_state(PetState.COMBAT)
            else:
                self.alchemy_time += 1
                if self.alchemy_time >= self.alchemy_target_time:
                    # 炼丹完成
                    self.is_alchemying = False
                    self.finish_alchemy()
                else:
                    self.set_state(PetState.ALCHEMY)
                    # 炼丹中不获取常规收益，或者获取少量
                    return # 跳过后续常规 update

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
                
    def start_alchemy(self):
        if self.is_alchemying:
            return
        
        self.is_alchemying = True
        self.alchemy_time = 0
        self.set_state(PetState.ALCHEMY)
        logger.info("开始闭关炼丹")
        self.show_notification("开始闭关炼丹... (请勿高频操作)")
        
    def finish_alchemy(self):
        import random
        # 炼丹产出
        pills = ["聚气丹", "筑基丹", "废丹"]
        # 权重
        weights = [60, 10, 30]
        result = random.choices(pills, weights=weights, k=1)[0]
        
        if result == "废丹":
             logger.info("炼丹完成: 废丹")
             self.show_notification("炼丹失败，得出一炉废丹。")
        else:
             logger.info(f"炼丹成功: {result}")
             self.cultivator.gain_item(result, 1)
             self.show_notification(f"丹成！获得 {result} x1")
        
        self.set_state(PetState.IDLE)
        QTimer.singleShot(2000, lambda: self.info_label.setText("准备修仙..."))

    def closeEvent(self, event):
        logger.info("程序关闭，保存数据...")
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
        
        # 4.5 特效层 (叠加在图片之上)
        from src.effect_widget import EffectWidget
        self.effect_widget = EffectWidget(self.image_container)
        self.effect_widget.resize(200, 200)
        self.effect_widget.move(0, 0)
        self.effect_widget.hide()
        
        # 5. 信息 Label (默认完全隐藏)
        self.info_label = QLabel(self)
        self.info_label.resize(280, 50)
        self.info_label.move(10, 10) # 顶部
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                font-weight: 900;
                qproperty-alignment: AlignCenter;
            }
        """)
        # 添加阴影效果
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(1, 1)
        self.info_label.setGraphicsEffect(shadow)
        
        self.info_label.hide() # 默认隐藏

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
        # 确保绘制是透明的
        pass 

    # --- 鼠标悬停交互 ---
    def enterEvent(self, event):
        # 鼠标移入：显示详细信息
        self.info_label.show()
        # msg, _ = self.cultivator.update(0) # 不调用 update，只获取属性
        # update 会触发经验增长，hover 不应该触发
        
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
        # 鼠标移出：隐藏
        self.info_label.hide()
        super().leaveEvent(event)
        
    def show_notification(self, text):
        # 显示通知时强制显示
        self.info_label.setText(text)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #00FF7F; 
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        self.info_label.show()
        
        # 2秒后如果鼠标不在上面，就隐藏
        QTimer.singleShot(2000, self.hide_notification)

    def hide_notification(self):
        # 如果鼠标不在窗口内，就隐藏
        if not self.underMouse():
            self.info_label.hide()
        else:
            # 如果鼠标还在，恢复成 hover 状态的显示 (避免通知文字一直卡着)
            self.enterEvent(None) # 重新触发一次 hover 刷新逻辑

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
            
        # ALCHEMY
        alchemy_path = os.path.join(assets_path, 'cultivator_alchemy.png')
        if os.path.exists(alchemy_path):
            self.state_images[PetState.ALCHEMY] = QPixmap(alchemy_path)

        # 默认显示 IDLE
        if PetState.IDLE in self.state_images:
            self.set_state(PetState.IDLE)
        else:
            logger.warning("资源缺失: cultivator_idle.png")
            self.info_label.setText("资源缺失")

    def set_state(self, state: PetState):
        if hasattr(self, 'state_images') and state in self.state_images:
            if getattr(self, 'current_state', None) != state:
                 logger.debug(f"切换状态: {state.name}")
            self.current_state = state
            pixmap = self.state_images[state]
            self.image_label.setPixmap(pixmap)
            
            # 设置遮罩，实现点击穿透透明区域
            # 注意：因为我们有浮动动画(Move)，mask 是相对于窗口坐标的
            # mask 需要跟随 image_container 的位置变化比较麻烦
            # 简单做法：我们只给 image_label 做 mask？不行，点击是 Window 接收的
            
            # 更好的方案：不依赖 mask，因为动画会导致 mask 频繁计算极其消耗性能
            # 方案 B：在 mousePressEvent 里手动判定点击位置是否透明
            
            # 这里我们还是先做基础的 mask 测试，如果 mask 不动的话。
            # 考虑到浮动范围很小，我们可以给整个 Window 一个稍微大一点的 Mask，或者暂时不 mask
            # 我们尝试给整个窗口设置 Mask，每次 float 更新时移动 mask？
            pass
            
        # 特效控制
        if state == PetState.ALCHEMY:
            self.effect_widget.start_fire()
        else:
            self.effect_widget.stop()

    # --- 鼠标拖拽逻辑 ---
    def mousePressEvent(self, event: QMouseEvent):
        # 手动判定是否点击在了图片的非透明区域
        # 1. 获取点击位置相对于 image_label 的坐标
        # event.position() 是相对于窗口 PetWindow 的
        click_pos = event.position().toPoint()
        
        # image_container 的位置
        container_pos = self.image_container.pos()
        
        # 相对坐标 (相对于 image_label/container 左上角)
        local_pos = click_pos - container_pos
        
        is_hit = False
        if hasattr(self, 'state_images') and self.current_state in self.state_images:
            pixmap = self.state_images[self.current_state]
            
            # Label 的大小 (200x200)
            lbl_w = self.image_label.width()
            lbl_h = self.image_label.height()
            
            # 检查坐标是否在 Label 范围内
            if 0 <= local_pos.x() < lbl_w and 0 <= local_pos.y() < lbl_h:
                # 关键修复：将 Label 坐标映射回原图 Pixmap 坐标
                # 因为 setScaledContents(True) 会把图片拉伸
                img = pixmap.toImage()
                pm_w = img.width()
                pm_h = img.height()
                
                if pm_w > 0 and pm_h > 0:
                    # 计算映射坐标
                    img_x = int(local_pos.x() * (pm_w / lbl_w))
                    img_y = int(local_pos.y() * (pm_h / lbl_h))
                    
                    # 边界检查
                    img_x = max(0, min(img_x, pm_w - 1))
                    img_y = max(0, min(img_y, pm_h - 1))
                    
                    color = img.pixelColor(img_x, img_y)
                    # print(f"Click at {local_pos}, map to {img_x},{img_y}, alpha={color.alpha()}") # Debug
                    if color.alpha() > 10: # 非透明
                        is_hit = True
                        
            # 【保底逻辑】
            # 如果像素检测没过（可能是去背去多了，或者是误判），
            # 我们强制给一个“核心区域”作为可点击区 (例如中间 60x100 的区域)
            center_rect_x = (lbl_w - 60) // 2
            center_rect_y = (lbl_h - 100) // 2
            if not is_hit:
                if (center_rect_x <= local_pos.x() <= center_rect_x + 60 and 
                    center_rect_y <= local_pos.y() <= center_rect_y + 100):
                    is_hit = True

        if not is_hit:
            # 如果没点中实体，忽略事件以尝试穿透
            event.ignore() 
            # 注意：在某些系统上，如果窗口没有设置 Mask，ignore 可能也不会穿透给桌面，
            # 而是直接被丢弃。但在 PyQt 顶层窗口中，ignore 通常意味着“我不处理”，
            # 如果是 Frameless，行为取决于 OS。
            # 如果依然无法穿透，说明必须用 setMask。
            # 但用户反馈的是“原本的小人无法拖动/右键”，说明 is_hit 判定失败了，所以我们优先修 is_hit。
            return # 既然没点中，就直接返回，不再执行下面的拖拽逻辑

        # 点中了，处理事件
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.press_pos = event.globalPosition().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()


    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            # 判断是否是点击 (移动距离很小)
            release_pos = event.globalPosition().toPoint()
            if hasattr(self, 'press_pos') and (release_pos - self.press_pos).manhattanLength() < 5:
                self.on_pet_clicked()
                
            event.accept()
            
    def on_pet_clicked(self):
        # 播放随机对话
        dialogue = self.cultivator.get_random_dialogue()
        self.show_notification(dialogue)
        
        # 简单的点击反馈动画 (例如稍微缩放一下，或者震动一下)
        # 这里用一个小跳跃模拟
        self.float_direction = -1
        self.float_y = -10 # 向上跳一下
            
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

        # 炼丹
        alchemy_action = QAction('闭关炼丹', self)
        alchemy_action.triggered.connect(self.start_alchemy)
        menu.addAction(alchemy_action)

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
