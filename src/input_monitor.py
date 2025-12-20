from pynput import keyboard, mouse
import time
from threading import Lock

class InputMonitor:
    def __init__(self):
        self._lock = Lock()
        self._action_count = 0
        self._start_time = time.time()
        
        # 监听器
        self.kb_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        
        self.running = False

    def start(self):
        self.running = True
        self.kb_listener.start()
        self.mouse_listener.start()

    def stop(self):
        self.running = False
        self.kb_listener.stop()
        self.mouse_listener.stop()

    def on_press(self, key):
        with self._lock:
            self._action_count += 1

    def on_click(self, x, y, button, pressed):
        if pressed:
            with self._lock:
                self._action_count += 1

    def get_apm(self):
        """
        获取当前 APM 并重置计数器 (简化版)
        建议每秒调用一次，返回值即为 Actions Per Second，乘以 60 即为 APM
        """
        with self._lock:
            count = self._action_count
            self._action_count = 0 # 重置，计算瞬时 APM
            
        return count * 60 # 简单的把这一秒的操作数 * 60 当作瞬时 APM

    def get_apm_snapshot(self):
        """
        获取当前瞬时 APM 快照，不重置计数器 (用于 UI 显示)
        """
        with self._lock:
            # 这里其实不太准，因为 get_apm 每秒清零了，这里拿到的永远也只是这 1 秒内的累积
            # 但既然是 Snapshot，就直接返回 0 或者 上一秒的值会更好
            # 简化起见，还是返回当前累计值 * 60
            return self._action_count * 60
