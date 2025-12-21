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
        
        # 监听器
        self.kb_listener = keyboard.Listener(on_press=self.on_press)
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
        with self._lock:
            self._kb_count += 1

    def on_click(self, x, y, button, pressed):
        if pressed:
            with self._lock:
                self._mouse_count += 1

    def on_scroll(self, x, y, dx, dy):
        with self._lock:
             # 滚轮也算鼠标操作
            self._mouse_count += 1

    def get_stats(self):
        """
        获取当前 键盘和鼠标 的操作计数，并重置计数器。
        建议每秒调用一次。
        Returns:
            (kb_apm, mouse_apm) - 其实是 Actions Per Minute (但这里返回数值直接用作判定即可)
        """
        with self._lock:
            kb = self._kb_count
            ms = self._mouse_count
            self._kb_count = 0
            self._mouse_count = 0
            
        # 转换为 Per Minute (如果每秒调用一次，则 * 60)
        return kb * 60, ms * 60
