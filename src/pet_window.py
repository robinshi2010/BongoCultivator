import sys
import os
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QMenu, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QPixmap, QAction, QMouseEvent, QCursor
from src.state import PetState
from src.input_monitor import InputMonitor
from src.services.activity_recorder import ActivityRecorder
from src.cultivator import Cultivator
from src.logger import logger
from src.utils.path_helper import get_resource_path, get_user_data_dir

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 核心数据
        logger.info("初始化 PetWindow...")
        self.cultivator = Cultivator()
        
        self.init_ui() # 必须先初始化UI
        
        # 路径处理
        self.save_path = os.path.join(get_user_data_dir(), 'save_data.json')
        
        self.cultivator.load_data(self.save_path)
        self.load_assets() # 只有在UI初始化后才能加载资源
        
        # 拖拽相关
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # 核心逻辑
        self.monitor = InputMonitor()
        monitor_started = self.monitor.start()
        if not monitor_started:
            self._maybe_prompt_input_permissions()
            
        # 启动活动记录器 (每分钟存库)
        self.recorder = ActivityRecorder(self.monitor)
        self.recorder.start()
        
        # 炼丹状态
        self.is_alchemying = False
        self.is_ascending = False
        self.alchemy_time = 0
        self.alchemy_target_time = 10
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(1000) # 1秒刷新一次
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(1000) # 1秒刷新一次
        
        self.idle_duration = 0 # 记录 IDLE 持续时间
        
        # Windows
        self.stats_window = None
        self.tray = None
        self.notifications_enabled = True

    def set_tray(self, tray):
        self.tray = tray

    def game_loop(self):
        # 0. 绝对优先级锁：如果正在渡劫/飞升/播放动画，完全暂停状态更新
        if getattr(self, 'is_ascending', False):
            # logger.debug("Game Loop Skipped: Ascending Lock is Active") 
            return

        # 1. 获取分离的统计数据
        kb_apm, mouse_apm = self.monitor.get_stats()
        
        # 混合总 APM 用于旧逻辑判断 (比如炼丹打断)
        total_apm = kb_apm + mouse_apm
        
        # 如果正在炼丹
        if self.is_alchemying:
            # 高 APM 会打断炼丹 (阈值提高到 200，即每秒 >3 次操作)
            if total_apm > 200:
                self.is_alchemying = False
                logger.warning(f"炼丹失败: APM过高 ({total_apm})")
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
                    # 炼丹中不获取常规收益
                    return 

        # 2. 调用新的 Cultivator 更新逻辑
        gain_msg, state_code = self.cultivator.update(kb_apm, mouse_apm)
        
        # 3. 状态映射 (Cultivator 返回的是 int code, 转为 Enum)
        # 0:IDLE, 1:COMBAT, 2:WORK, 3:READ
        target_state = PetState.IDLE
        if state_code == 1:
            target_state = PetState.COMBAT
            # 触发粒子: 爆发模式
            self.effect_widget.set_mode("combat") # 预留
        elif state_code == 2:
            target_state = PetState.WORK
            self.effect_widget.set_mode("work")   # 预留
        elif state_code == 3:
            target_state = PetState.READ
            self.effect_widget.set_mode("read")   # 预留
        else:
            target_state = PetState.IDLE
            self.effect_widget.set_mode("idle")   # 预留
            
        # 切换状态 (如果不是炼丹状态)
        if not self.is_alchemying and not getattr(self, 'is_ascending', False):
            if self.current_state != target_state:
                self.set_state(target_state)
            
            # Idle Sleep Logic
            if target_state == PetState.IDLE:
                self.idle_duration += 1
                if self.idle_duration > 60: # 60s without input -> Sleep
                    if hasattr(self, 'extra_images') and 'sleep' in self.extra_images:
                        self.image_label.setPixmap(self.extra_images['sleep'])
            else:
                self.idle_duration = 0 # Reset on activity
        
        # 4. Update Tray Tooltip
        if self.tray:
            # Format: 【筑基期】 EXP/MAX | 灵石: 100 | 状态: 历练
            state_cn = {
                PetState.IDLE: "闭关", PetState.WORK: "历练",
                PetState.READ: "悟道", PetState.COMBAT: "斗法",
                PetState.ALCHEMY: "炼丹", PetState.ASCEND: "渡劫"
            }.get(self.current_state, "未知")
            
            tooltip = (
                f"【{self.cultivator.current_layer}】\n"
                f"修为: {self.cultivator.exp}/{self.cultivator.max_exp}\n"
                f"灵石: {self.cultivator.money}\n"
                f"状态: {state_cn}"
            )
            self.tray.set_tooltip(tooltip)

        # 5. 检查事件日志
        state_cn = { # Re-map for logic if needed or just pass
             # ... existing logic ...
        }
        # Simplify checking events
        if self.cultivator.events:
            latest_event = self.cultivator.events[-1]
            self.show_notification(latest_event)
            self.cultivator.events.clear()
                
    def set_always_on_top(self, enabled: bool):
        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show() # setWindowFlags hides the window, need to show again

    def toggle_notifications(self, enabled: bool):
        from src.logger import logger
        logger.info(f"对话框显示状态切换: {self.notifications_enabled} -> {enabled}")
        self.notifications_enabled = enabled
        if not enabled:
            self.info_label.hide()

    # --- 辅助方法: 计算窗口安全位置 (防止超出屏幕) ---
    def _calculate_safe_pos(self, widget, prefer_side='right'):
        pet_geo = self.frameGeometry()
        
        # Multi-monitor fix: Use the screen where the PetWindow currently is
        current_screen = self.screen()
        if not current_screen:
             current_screen = QApplication.primaryScreen()
             
        screen_geo = current_screen.geometry()
        
        w = widget.width()
        h = widget.height()
        
        # X 轴处理
        if prefer_side == 'right':
            # 优先尝试右边
            x = pet_geo.right() + 10
            # 如果右边放不下，放左边
            if x + w > screen_geo.right():
                x = pet_geo.left() - w - 10
        else: # prefer 'left'
            # 优先尝试左边
            x = pet_geo.left() - w - 10
            # 如果左边放不下，放右边
            if x < screen_geo.left():
                x = pet_geo.right() + 10
                
        # 兜底: 如果还是出界 (窗口太宽)，则强制显示在屏幕内
        if x < screen_geo.left(): 
            x = screen_geo.left() + 10
        elif x + w > screen_geo.right():
            x = screen_geo.right() - w - 10

        # Y 轴处理 (防止底部被遮挡)
        # 默认顶部对齐
        y = pet_geo.top()
        
        # 如果底部超出了屏幕底部
        if y + h > screen_geo.bottom():
             # 向上移动，底部对齐屏幕底部 (留出少许边距)
             y = screen_geo.bottom() - h - 10
             
        # 兜底: 防止顶部出界
        if y < screen_geo.top():
            y = screen_geo.top() + 10
            
        return x, y

    def open_alchemy_window(self):
        from src.alchemy_window import AlchemyWindow
        if not hasattr(self, 'alchemy_window') or self.alchemy_window is None:
            self.alchemy_window = AlchemyWindow(self.cultivator, self)
            
        # 统一使用安全定位，放在右侧 (和背包一侧，方便查看材料)
        x, y = self._calculate_safe_pos(self.alchemy_window, prefer_side='right')
        self.alchemy_window.move(x, y)
        self.alchemy_window.show()

    def open_stats_window(self):
        from src.ui.stats_window import StatsWindow
        if self.stats_window is None:
            self.stats_window = StatsWindow(cultivator=self.cultivator)
            
        # 使用新的安全定位 (默认右边)
        x, y = self._calculate_safe_pos(self.stats_window, prefer_side='right')
        self.stats_window.move(x, y)
        
        self.stats_window.show()
        self.stats_window.raise_()
        self.stats_window.activateWindow()

    def start_alchemy_task(self, target_pill_id):
        if self.is_alchemying: return
        
        self.is_alchemying = True
        self.alchemy_time = 0
        self.current_crafting_id = target_pill_id
        
        # 不同丹药耗时不同？暂时统一 10s
        self.alchemy_target_time = 10 
        
        self.set_state(PetState.ALCHEMY)
        logger.info(f"开始炼制: {target_pill_id}")
        self.show_notification("开始闭关炼丹... (请勿高频操作)")

    def open_inventory(self):
        # 延迟导入防止循环依赖
        from src.inventory_window import InventoryWindow
        
        # 单例/缓存处理：如果还没创建过，就创建
        if not hasattr(self, 'inventory_window') or self.inventory_window is None:
            self.inventory_window = InventoryWindow(self.cultivator, pet_window=self) # parent=None 保证它是独立窗口，不受主窗口裁剪限制
            
        x, y = self._calculate_safe_pos(self.inventory_window, prefer_side='right')
        self.inventory_window.move(x, y)
        
        self.inventory_window.show()
        self.inventory_window.refresh_list() # 刷新数据

    def open_market(self):
        from src.market_window import MarketWindow
        
        if not hasattr(self, 'market_window') or self.market_window is None:
            self.market_window = MarketWindow(self.cultivator, None)
            
        x, y = self._calculate_safe_pos(self.market_window, prefer_side='left')
        self.market_window.move(x, y)
        self.market_window.show()

    def open_talent_window(self):
        from src.talent_window import TalentWindow
        
        if not hasattr(self, 'talent_window') or self.talent_window is None:
            self.talent_window = TalentWindow(self.cultivator, None)
            
        x, y = self._calculate_safe_pos(self.talent_window, prefer_side='left')
        self.talent_window.move(x, y)
        self.talent_window.show()



    def finish_alchemy(self):
        import random
        
        target_id = getattr(self, 'current_crafting_id', None)
        if not target_id:
            # Fallback for legacy (should not happen with UI)
            self._legacy_finish_alchemy()
            return
            
        target_info = self.cultivator.item_manager.get_item(target_id)
        name = target_info["name"]
        
        # 成功率判定 (越高级越难?)
        # 暂时简单处理: 80% 成功率 (因为材料已经扣了，太容易失败会很挫败)
        success_rate = 0.8
        
        if random.random() < success_rate:
            logger.info(f"炼丹成功: {name}")
            self.cultivator.gain_item(target_id, 1)
            self.show_notification(f"丹成！获得 {name} x1")
            
            # 粒子特效: 成功金光
            # self.effect_widget.show_success() # TODO
        else:
            logger.info("炼丹失败: 废丹")
            self.cultivator.gain_item("pill_waste", 1) # 假如有废丹ID，或者就不给东西
            self.show_notification("炼丹失败，材料化为乌有...")
            
        self.is_alchemying = False
        self.set_state(PetState.IDLE)
        # 恢复默认style，防止背景残留（虽然用了transparent，但更保险）
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                font-weight: 900;
                qproperty-alignment: AlignCenter;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        QTimer.singleShot(2000, lambda: self.info_label.setText("准备修仙..."))
        
    def _legacy_finish_alchemy(self):
        # ... (旧逻辑备份，或者直接删除) ...
        self.is_legacy_alchemying = False # Changed variable name to avoid conflict if really needed, but it's legacy
        self.set_state(PetState.IDLE)

    def closeEvent(self, event):
        logger.info("程序关闭，保存数据...")
        self.cultivator.save_data(self.save_path)
        if hasattr(self, 'recorder'):
            self.recorder.stop()
        self.monitor.stop()
        super().closeEvent(event)

    def init_ui(self):
        # 1. 窗口属性设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # 无边框
            Qt.WindowType.WindowStaysOnTopHint |      # 始终置顶
            Qt.WindowType.Tool |                      # 工具窗口 (不在任务栏显示)
            Qt.WindowType.WindowDoesNotAcceptFocus    # 不抢占焦点(关键!)
        )
        
        # 2. 核心透明设置 (macOS 关键)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True) 
        self.setStyleSheet("background: transparent;")

        # 3. 初始位置与大小
        self.resize(300, 350)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 350, screen.height() - 400)

        # 4. 图片容器 (用于动画)
        self.image_container = QWidget(self)
        self.image_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.image_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
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
        self.effect_widget.request_shake.connect(self.on_shake_requested)
        
        # 5. 信息 Label (默认完全隐藏)
        self.info_label = QLabel(self)
        # 不再硬性限制高度为 50，给足空间或者后续自适应
        self.info_label.setFixedWidth(280) 
        self.info_label.move(10, 10) # 顶部
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                font-weight: 900;
                qproperty-alignment: AlignCenter;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        # 添加阴影效果
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15) # 加大模糊半径
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 0)
        self.info_label.setGraphicsEffect(shadow)
        
        self.info_label.hide() # 默认隐藏
        self.info_label.setWordWrap(True)

        # 6. 呼吸/悬浮动画定时器
        self.float_timer = QTimer(self)
        self.float_timer.timeout.connect(self.update_floating_animation)
        self.float_timer.start(50) # 20fps
        
        self.float_y = 0
        self.float_direction = 1
        self.base_y = 60 # 图片的基础 Y 坐标
        
    def reset_position(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 350, screen.height() - 400)
        self.show()
        
    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "darwin":
            QTimer.singleShot(0, self._apply_macos_window_settings)
            QTimer.singleShot(150, self._apply_macos_window_settings)

    def _macos_get_ns_window(self):
        if sys.platform != "darwin":
            return None

        try:
            import ctypes
            from ctypes import c_char_p, c_void_p
            from ctypes.util import find_library
        except Exception as exc:
            logger.warning(f"macOS 窗口初始化失败: {exc}")
            return None

        libobjc_path = find_library("objc")
        if not libobjc_path:
            logger.warning("macOS 窗口初始化失败: 找不到 libobjc")
            return None

        try:
            libobjc = ctypes.cdll.LoadLibrary(libobjc_path)
            sel_register_name = libobjc.sel_registerName
            sel_register_name.restype = c_void_p
            sel_register_name.argtypes = [c_char_p]

            objc_msg_send = libobjc.objc_msgSend

            def send(receiver, selector, *args, restype=c_void_p, argtypes=None):
                objc_msg_send.restype = restype
                objc_msg_send.argtypes = [c_void_p, c_void_p] + (argtypes or [])
                return objc_msg_send(receiver, selector, *args)

            wid = int(self.winId())
            if wid == 0:
                return None

            ns_view = c_void_p(wid)
            ns_window = send(ns_view, sel_register_name(b"window"), restype=c_void_p)
            if not ns_window:
                return None

            return ns_window, send, sel_register_name
        except Exception as exc:
            logger.warning(f"macOS 窗口初始化失败: {exc}")
            return None

    def _apply_macos_window_settings(self):
        if sys.platform != "darwin":
            return

        try:
            import ctypes
            from ctypes import c_bool, c_int, c_long, c_ulong
            from ctypes.util import find_library
        except Exception as exc:
            logger.warning(f"macOS 窗口设置失败: {exc}")
            return

        result = self._macos_get_ns_window()
        if not result:
            return

        ns_window, send, sel_register_name = result

        try:
            sel_ignore = sel_register_name(b"setIgnoresMouseEvents:")
            send(ns_window, sel_ignore, c_bool(False), restype=None, argtypes=[c_bool])
        except Exception as exc:
            logger.warning(f"macOS 点击穿透设置失败: {exc}")

        try:
            sel_hides = sel_register_name(b"setHidesOnDeactivate:")
            send(ns_window, sel_hides, c_bool(False), restype=None, argtypes=[c_bool])
        except Exception as exc:
            logger.warning(f"macOS Deactivate 设置失败: {exc}")

        try:
            sel_set_behavior = sel_register_name(b"setCollectionBehavior:")
            NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
            NSWindowCollectionBehaviorStationary = 1 << 4
            NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8
            behavior = (
                NSWindowCollectionBehaviorCanJoinAllSpaces
                | NSWindowCollectionBehaviorStationary
                | NSWindowCollectionBehaviorFullScreenAuxiliary
            )
            send(ns_window, sel_set_behavior, c_ulong(behavior), restype=None, argtypes=[c_ulong])
        except Exception as exc:
            logger.warning(f"macOS 窗口空间设置失败: {exc}")

        try:
            core_graphics_path = find_library("CoreGraphics")
            if not core_graphics_path:
                logger.warning("macOS 置顶设置失败: 找不到 CoreGraphics")
                return

            core_graphics = ctypes.cdll.LoadLibrary(core_graphics_path)
            cg_window_level_for_key = core_graphics.CGWindowLevelForKey
            cg_window_level_for_key.argtypes = [c_int]
            cg_window_level_for_key.restype = c_int

            # Check if AlwaysStatusTop is enabled in Qt flags
            should_be_on_top = bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
            
            # Normal level = 0, Floating = 5
            kCGNormalWindowLevelKey = 0
            kCGFloatingWindowLevelKey = 5
            
            level_key = kCGFloatingWindowLevelKey if should_be_on_top else kCGNormalWindowLevelKey
            level = cg_window_level_for_key(level_key)

            sel_set_level = sel_register_name(b"setLevel:")
            send(ns_window, sel_set_level, c_long(level), restype=None, argtypes=[c_long])
        except Exception as exc:
            logger.warning(f"macOS 置顶设置失败: {exc}")

        try:
            sel_order_front = sel_register_name(b"orderFrontRegardless")
            send(ns_window, sel_order_front, restype=None)
        except Exception as exc:
            logger.warning(f"macOS 置顶前置失败: {exc}")

    def _maybe_prompt_input_permissions(self):
        if sys.platform != "darwin":
            return

        if self.monitor.permission_denied:
            message = (
                "需要启用输入监听权限才能捕获键盘/鼠标动作。\n\n"
                "请前往：系统设置 > 隐私与安全性 > 输入监控\n"
                "并允许当前应用或 python 进程。\n\n"
                "如仍无效，请同时开启“辅助功能”权限。"
            )
        elif self.monitor.last_error:
            message = (
                "全局输入监听启动失败。\n\n"
                "请检查：系统设置 > 隐私与安全性 > 输入监控。\n"
                "必要时也开启“辅助功能”权限。"
            )
        else:
            return

        logger.warning("全局输入监听未就绪，提示权限设置")
        QMessageBox.information(None, "需要输入监听权限", message)

    def update_floating_animation(self):
        # 简单的上下浮动 (Sin 也可以，这里用简单的增量)
        if self.current_state == PetState.IDLE:
            speed = 0.5
            range_limit = 10
        else:
            speed = 0.2 # 战斗时浮动更快
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
        # 鼠标移入：不再显示详细属性，保持清爽 (Plan 6)
        # 仅当有通知时显示通知，或者是交互提示
        # self.info_label.show() 
        super().enterEvent(event)

    def leaveEvent(self, event):
        # 鼠标移出：隐藏
        self.info_label.hide()
        super().leaveEvent(event)
        
    def show_notification(self, text):
        if not self.notifications_enabled:
            return

        # 显示通知时强制显示
        self.info_label.setText(text)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #00FF7F; 
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 150); /* 增加黑色半透明背景 */
                border-radius: 5px;
                padding: 4px;
            }
        """)
        
        # 核心修复：根据文本自适应大小和居中
        self.info_label.adjustSize()
        new_width = self.info_label.width()
        
        # 限制最大宽度，防止太宽
        max_width = self.width() - 20 # 左右留边
        if new_width > max_width:
            self.info_label.setFixedWidth(max_width) # 定宽会让 Label 重新计算换行
            self.info_label.adjustSize()             # 重新计算高度
        
        # 居中
        new_x = (self.width() - self.info_label.width()) // 2
        self.info_label.move(new_x, 10)
        
        self.info_label.show()
        
        # 动态显示时长: 基础 3秒 + 每字 0.2秒
        duration = 3000 + len(text) * 200
        QTimer.singleShot(duration, self.hide_notification)

    def hide_notification(self):
        # 只有在非悬停状态下隐藏? 
        # Plan 6: 实际上是对话框模式，显示完了就消失，不需要一直在
        self.info_label.hide()

    def load_assets(self):
        # 资源路径
        assets_path = get_resource_path('assets')
        
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
            
        # ALCHEMY (Load variants)
        self.alchemy_images = {}
        for variant in ['low', 'mid', 'high']:
            path = os.path.join(assets_path, f'cultivator_alchemy_{variant}.png')
            if os.path.exists(path):
                self.alchemy_images[variant] = QPixmap(path)
        
        # Fallback alchemy default
        alc_path = os.path.join(assets_path, 'cultivator_alchemy.png')
        if os.path.exists(alc_path):
             self.state_images[PetState.ALCHEMY] = QPixmap(alc_path)

        # WORK (Use walk as default)
        work_path = os.path.join(assets_path, 'cultivator_walk.png')
        if os.path.exists(work_path):
             self.state_images[PetState.WORK] = QPixmap(work_path)

        # TRIBULATION
        # TRIBULATION
        self.tribulation_images = {}
        # Load all specific 0-8 images defined in Plan 12
        trib_names = [
            'tribulation_0_foundation.png', # Lv0 -> Lv1
            'tribulation_1_goldcore.png',   # Lv1 -> Lv2
            'tribulation_2_nascentsoul.png',# Lv2 -> Lv3
            'tribulation_3_divine.png',     # Lv3 -> Lv4
            'tribulation_4_void.png',       # Lv4 -> Lv5
            'tribulation_5_integration.png',# Lv5 -> Lv6
            'tribulation_6_mahayana.png',   # Lv6 -> Lv7
            'tribulation_7_calamity.png',   # Lv7 -> Lv8
            'tribulation_8_ascension.png'   # Lv8 -> Lv9
        ]
        
        for i, filename in enumerate(trib_names):
            path = os.path.join(assets_path, filename)
            if os.path.exists(path):
                self.tribulation_images[i] = QPixmap(path)
        
        logger.info(f"Tribulation images loaded: {len(self.tribulation_images)}")
        
        # Fallback / Generic Tribulation if needed (user didn't provide generic yet, but we can reuse high alchemy or combat?)
        # For now, if missing, it falls back to IDLE in set_state

        # WORK (Use walk as default)
        work_path = os.path.join(assets_path, 'cultivator_walk.png')
        if os.path.exists(work_path):
             self.state_images[PetState.WORK] = QPixmap(work_path)

        # READ
        read_path = os.path.join(assets_path, 'cultivator_read.png')
        if os.path.exists(read_path):
             self.state_images[PetState.READ] = QPixmap(read_path)

        # Extra optional assets
        self.extra_images = {}
        for name in ['drag', 'sleep', 'walk']:
            path = os.path.join(assets_path, f'cultivator_{name}.png')
            if os.path.exists(path):
                self.extra_images[name] = QPixmap(path)

        # 默认显示 IDLE
        if PetState.IDLE in self.state_images:
            self.set_state(PetState.IDLE)
        else:
            logger.warning("资源缺失: cultivator_idle.png")
            self.info_label.setText("资源缺失")

    def set_state(self, state: PetState):
        if hasattr(self, 'state_images'):
            if getattr(self, 'current_state', None) != state:
                 logger.debug(f"切换状态: {state.name}")
            self.current_state = state
            
            pixmap = None
            
            # Special handling for Alchemy Tier
            if state == PetState.ALCHEMY and hasattr(self, 'alchemy_images'):
                idx = self.cultivator.layer_index
                if idx <= 2:
                    pixmap = self.alchemy_images.get('low')
                elif idx <= 5:
                    pixmap = self.alchemy_images.get('mid')
                else:
                    pixmap = self.alchemy_images.get('high')
            
            # Special handling for Tribulation (ASCEND)
            elif state == PetState.ASCEND and hasattr(self, 'tribulation_images'):
                # 使用 layer_index - 1 是因为渡劫图代表的是"从哪个等级突破"
                # 例如：从 Lv0 升 Lv1，应该显示 tribulation_0 (炼气渡劫)
                # 但此时 layer_index 已经变成 1 了，所以要减 1
                idx = max(0, self.cultivator.layer_index - 1)
                
                # Try to find exact match or fallback to lower levels
                target_idx = idx
                found_trib = False
                while target_idx >= 0:
                    if target_idx in self.tribulation_images:
                        pixmap = self.tribulation_images[target_idx]
                        found_trib = True
                        break
                    target_idx -= 1
                
                if not found_trib:
                    # Force fallback to any available image
                    if 0 in self.tribulation_images:
                        pixmap = self.tribulation_images[0]
                    elif self.tribulation_images:
                        first_key = list(self.tribulation_images.keys())[0]
                        pixmap = self.tribulation_images[first_key]
                
                # If still no pixmap, fallback will happen below

            # Fallback to standard logic
            if not pixmap:
                pixmap = self.state_images.get(state)
            
            # Final fallback to IDLE
            if not pixmap and PetState.IDLE in self.state_images:
                pixmap = self.state_images[PetState.IDLE]
            
            if pixmap:
                self.image_label.setPixmap(pixmap)
            
            # Update effect mode
            mode_map = {
                PetState.IDLE: "idle",
                PetState.WORK: "work",
                PetState.READ: "read",
                PetState.COMBAT: "combat",
                PetState.ALCHEMY: "alchemy",
                PetState.ASCEND: "tribulation"
            }
            effect_mode = mode_map.get(state, "idle")
            self.effect_widget.set_mode(effect_mode)

    # --- 鼠标拖拽逻辑 ---
    # ... (Keep existing layout) ...
    # Skip lines until input_secret to override it

    def input_secret(self):
        from src.ui.custom_input import DarkInputDialog
        text, ok = DarkInputDialog.get_text(self, "天机", "请输入密令:")
        
        if ok and text:
            old_layer = self.cultivator.layer_index
            success, msg = self.cultivator.process_secret_command(text)
            new_layer = self.cultivator.layer_index
            
            self.show_notification(msg)
            
            if success:
                # If level up happened
                if new_layer > old_layer:
                    self.is_ascending = True
                    
                    # Show visual effect sequence
                    # 1. Tribulation visuals (briefly)
                    self.set_state(PetState.ASCEND)
                    self.effect_widget.trigger_tribulation()
                    
                    # 2. Success Effect after 2s
                    QTimer.singleShot(2000, self.effect_widget.trigger_breakthrough_success)
                    def end_secret_ascend():
                        self.is_ascending = False
                        self.set_state(PetState.IDLE)
                    QTimer.singleShot(3000, end_secret_ascend)
                else:
                    # Just simple success (e.g. money reset)
                     if "已转世" not in msg:
                        self.effect_widget.trigger_breakthrough_success()

    def on_attempt_breakthrough(self):
        # 1. Trigger Visuals FIRST
        self.is_ascending = True
        self.set_state(PetState.ASCEND)
        self.effect_widget.trigger_tribulation()
        self.show_notification("天劫降临... (渡劫中)")
        
        # 2. Delay calculation by 3 seconds
        QTimer.singleShot(3000, self._finalize_breakthrough)

    def _finalize_breakthrough(self):
        success, msg = self.cultivator.attempt_breakthrough()
        self.show_notification(msg)
        
        def end_ascend():
            self.is_ascending = False
            self.set_state(PetState.IDLE)

        if success:
            # 3. Success Effect
            self.effect_widget.trigger_breakthrough_success()
            # Revert to idle after some time
            QTimer.singleShot(2000, end_ascend)
        else:
            # Failed
            QTimer.singleShot(1000, end_ascend)

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
            
            # Switch to drag image if available
            if hasattr(self, 'extra_images') and 'drag' in self.extra_images:
                self.image_label.setPixmap(self.extra_images['drag'])
            
            # Click effect
            self.effect_widget.emit_click_effect(local_pos.x(), local_pos.y())
            
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
            
            # Restore state image
            self.set_state(self.current_state)
            
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
                background-color: rgba(0, 0, 0, 0);
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
        
        if self.cultivator.can_breakthrough():
            break_action = QAction('⚡ 渡劫突破 ⚡', self)
            break_action.triggered.connect(self.on_attempt_breakthrough)
            menu.addAction(break_action)
        else:
            status_action = QAction(f'境界: {self.cultivator.current_layer}', self)
            status_action.triggered.connect(self.open_talent_window) # 点击境界打开属性面板
            menu.addAction(status_action)
            
        # 额外加一个属性入口
        talent_action = QAction('凝神内视', self)
        talent_action.triggered.connect(self.open_talent_window)
        menu.addAction(talent_action)
        
        # 统计数据
        stats_action = QAction('修仙记录', self)
        stats_action.triggered.connect(self.open_stats_window)
        menu.addAction(stats_action)
        
        menu.addSeparator()

        # 炼丹
        alchemy_action = QAction('开炉炼丹', self)
        alchemy_action.triggered.connect(self.open_alchemy_window)
        menu.addAction(alchemy_action)

        # 打开背包 - 动态命名
        # 化神期(4)及以上叫储物戒指，否则叫储物袋
        bag_name = '储物戒指' if self.cultivator.layer_index >= 4 else '储物袋'
        bag_action = QAction(bag_name, self)
        bag_action.triggered.connect(self.open_inventory)
        menu.addAction(bag_action)
        
        # 坊市 - 动态命名
        # 化神期(4)及以上叫多宝阁，否则叫修仙坊市
        market_name = '多宝阁' if self.cultivator.layer_index >= 4 else '修仙坊市'
        market_action = QAction(market_name, self)
        market_action.triggered.connect(self.open_market)
        menu.addAction(market_action)
        
        menu.addSeparator()
        
        # 隐秘入口
        secret_action = QAction('天机', self)
        secret_action.triggered.connect(self.input_secret)
        menu.addAction(secret_action)
        
        # 轮回
        if self.cultivator.layer_index >= 2: # 金丹以上才允许主动重修?
            rebirth_action = QAction('兵解重修', self)
            rebirth_action.triggered.connect(self.on_voluntary_rebirth)
            menu.addAction(rebirth_action)

        quit_action = QAction('云游四海 (退出)', self) # 原: 归隐山林
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec(pos)

    def on_voluntary_rebirth(self):
        from src.ui.custom_dialog import ConfirmationDialog
        from src.services.reincarnation_manager import ReincarnationManager
        
        reply = ConfirmationDialog.confirm(self, '兵解重修', 
                                     "你确定要兵解重修吗？\n当前修为将清空，但保留大部分气运(AP)。\n这将开始新的轮回。",
                                     "兵解", "取消")
        
        if reply:
             success, res = ReincarnationManager.perform_reincarnation(self.cultivator, "rebirth")
             if success:
                 self.show_notification(f"重修成功！继承气运: {res['legacy_points']}")
                 self.set_state(PetState.IDLE)

    def handle_death(self):
         from src.services.reincarnation_manager import ReincarnationManager
         from PyQt6.QtWidgets import QMessageBox
         
         # 先计算预览
         legacy = ReincarnationManager.calculate_inheritance(self.cultivator, "death")
         
         QMessageBox.critical(self, "身死道消", 
             f"渡劫失败，肉身崩坏！\n你已身死道消...\n\n即将进入轮回。\n继承气运: {legacy['legacy_points']} (继承率 {int(legacy['rate_used']*100)}%)",
             QMessageBox.StandardButton.Ok)
         
         ReincarnationManager.perform_reincarnation(self.cultivator, "death")
         self.set_state(PetState.IDLE)
         self.show_notification("转世重生，再踏仙途...")



    # --- Window Shake Logic ---
    def on_shake_requested(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_end_time = QTimer.singleShot(duration, self.stop_shake)
        
        if not hasattr(self, 'shake_timer'):
            self.shake_timer = QTimer(self)
            self.shake_timer.timeout.connect(self.do_shake)
            
        self.shake_timer.start(50)
        self.original_pos = self.pos()

    def do_shake(self):
        import random
        dx = random.randint(-self.shake_intensity, self.shake_intensity)
        dy = random.randint(-self.shake_intensity, self.shake_intensity)
        self.move(self.original_pos.x() + dx, self.original_pos.y() + dy)

    def stop_shake(self):
        if hasattr(self, 'shake_timer'):
            self.shake_timer.stop()
        if hasattr(self, 'original_pos'):
            self.move(self.original_pos)

    # --- Plan 46: 轮回转世 (进度导出/导入) ---
    def trigger_export_progress(self):
        """
        触发进度导出 - "轮回留痕"
        弹出文件保存对话框，将进度导出为 JSON 文件
        """
        from PyQt6.QtWidgets import QFileDialog
        from src.services.progress_exporter import ProgressExporter
        
        # 生成默认文件名
        default_filename = ProgressExporter.get_default_filename()
        
        # 弹出保存对话框
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "轮回留痕 - 导出进度",
            default_filename,
            "存档文件 (*.json);;所有文件 (*.*)"
        )
        
        if not filepath:
            return  # 用户取消
        
        # 确保文件扩展名
        if not filepath.endswith('.json'):
            filepath += '.json'
        
        # 执行导出
        success, message = ProgressExporter.export_progress(self.cultivator, filepath)
        
        if success:
            self.show_notification(message)
        else:
            from src.ui.custom_dialog import ConfirmationDialog
            ConfirmationDialog.alert(self, "导出失败", message)
    
    def trigger_import_progress(self):
        """
        触发进度导入 - "转世归来"
        弹出确认对话框和文件选择对话框，从 JSON 文件导入进度
        """
        from PyQt6.QtWidgets import QFileDialog
        from src.ui.custom_dialog import ConfirmationDialog
        from src.services.progress_exporter import ProgressExporter
        
        # 先确认
        reply = ConfirmationDialog.confirm(
            self, 
            "转世归来", 
            "此操作将覆盖当前所有进度！\n确定要从存档文件恢复进度吗？",
            "确定转世",
            "取消"
        )
        
        if not reply:
            return  # 用户取消
        
        # 弹出文件选择对话框
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "转世归来 - 导入进度",
            "",
            "存档文件 (*.json);;所有文件 (*.*)"
        )
        
        if not filepath:
            return  # 用户取消
        
        # 执行导入
        success, message = ProgressExporter.import_progress(self.cultivator, filepath)
        
        if success:
            # 刷新 UI 状态
            self.set_state(PetState.IDLE)
            self.show_notification(message)
            
            # 刷新打开的子窗口（如果有）
            if hasattr(self, 'inventory_window') and self.inventory_window and self.inventory_window.isVisible():
                self.inventory_window.refresh_inventory()
            if hasattr(self, 'market_window') and self.market_window and self.market_window.isVisible():
                self.market_window.refresh_display()
        else:
            ConfirmationDialog.alert(self, "导入失败", message)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = PetWindow()
    pet.show()
    sys.exit(app.exec())
