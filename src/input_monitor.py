from pynput import keyboard, mouse
import time
from threading import Lock

class InputMonitor:
    def __init__(self):
        self._lock = Lock()
        self._kb_count = 0
        self._mouse_count = 0
        self._start_time = time.time()
        self.last_error = None
        self.permission_denied = False
        
        # Debounce: Track currently pressed keys
        self.pressed_keys = set()
        
        # 滑动窗口记录 (最近 5 次调用的数据)
        # 如果 get_stats 每秒调用一次，平滑窗口就是 5 秒
        from collections import deque
        self.history_size = 5
        self.kb_history = deque(maxlen=self.history_size)
        self.mouse_history = deque(maxlen=self.history_size)
        
        # 累积计数 (用于数据持久化，独立于 APM 计算)
        self._acc_kb_count = 0
        self._acc_mouse_count = 0
        
        # 监听器
        self.kb_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.kb_listener.daemon = True
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.mouse_listener.daemon = True
        
        self.running = False

    def start(self):
        self.running = True
        self.last_error = None
        self.permission_denied = False
        self.pressed_keys.clear()
        
        # 清空历史
        self.kb_history.clear()
        self.mouse_history.clear()
        
        try:
            self.kb_listener.start()
            self.mouse_listener.start()
        except Exception as exc:
            self.last_error = exc
            message = str(exc)
            if "not trusted" in message.lower() or "operation not permitted" in message.lower():
                self.permission_denied = True
            self.running = False
            try:
                self.kb_listener.stop()
            except Exception:
                pass
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            return False
        return True

    def stop(self):
        self.running = False
        self.kb_listener.stop()
        self.mouse_listener.stop()

    def on_press(self, key):
        # 使用 key hash 或 str 作为 ID
        # key 可以是 KeyCode 或 Key 对象
        try:
            k_id = key.char
        except AttributeError:
            k_id = str(key)
            
        with self._lock:
            # 如果按键已经在集合中，说明是长按重复的一帧，忽略
            if k_id in self.pressed_keys:
                return
            
            self.pressed_keys.add(k_id)
            self._kb_count += 1
            self._acc_kb_count += 1
            
    def on_release(self, key):
        try:
            k_id = key.char
        except AttributeError:
            k_id = str(key)
            
        with self._lock:
            if k_id in self.pressed_keys:
                self.pressed_keys.remove(k_id)

    def on_click(self, x, y, button, pressed):
        if pressed:
            with self._lock:
                self._mouse_count += 1
                self._acc_mouse_count += 1

    def on_scroll(self, x, y, dx, dy):
        with self._lock:
             # 滚轮也算鼠标操作
            self._mouse_count += 1
            self._acc_mouse_count += 1

    def get_stats(self):
        """
        获取过去 N 秒的平均 APM (滑动窗口)。
        建议每秒调用一次。
        """
        with self._lock:
            current_kb = self._kb_count
            current_ms = self._mouse_count
            self._kb_count = 0
            self._mouse_count = 0
            
        # 存入历史窗口
        self.kb_history.append(current_kb)
        self.mouse_history.append(current_ms)
        
        # 计算窗口内的总数
        # 如果历史数据不足窗口大小，则按实际时间缩放? 
        # 简单起见，按 len(history) 缩放
        # APM = (Total / Seconds) * 60
        
        valid_seconds = len(self.kb_history)
        if valid_seconds == 0:
            return 0, 0
            
        avg_kb = sum(self.kb_history) / valid_seconds * 60
        avg_ms = sum(self.mouse_history) / valid_seconds * 60
            
        return int(avg_kb), int(avg_ms)

    def pop_accumulated_counts(self):
        """
        获取并重置累积计数 (用于数据库写入)
        """
        with self._lock:
            kb = self._acc_kb_count
            ms = self._acc_mouse_count
            self._acc_kb_count = 0
            self._acc_mouse_count = 0
        return kb, ms
