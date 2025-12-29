import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.pet_window import PetWindow
from src.logger import logger  # 初始化日志
from src.tray_icon import SystemTray

import signal
import sys

def main():
    logger.info("启动应用程序...")
    app = QApplication(sys.argv)
    
    # 防止关闭唯一的可视窗口 (StatsWindow) 时导致程序退出
    # 因为 PetWindow 是 Tool 类型，不被视为 Primary Window
    app.setQuitOnLastWindowClosed(False)
    
    # 可以在这里做一些全局配置，比如样式表
    
    # 1. 初始化/检查数据
    from src.services.data_loader import DataLoader
    from src.item_manager import ItemManager
    
    # 简单的检查: 实例化 ItemManager 会尝试加载，如果失败则 DataLoader
    # 但由于 ItemManager 是 lazy load，我们在 main 显示调用一次确保数据准备好
    # 或者直接调用 DataLoader.load_initial_data() ? ItemManager 内部有逻辑
    # 让我们更明确一点：
    im = ItemManager()
    if not im.flat_items:
        logger.info("主程序检测到数据为空，执行初始化...")
        DataLoader.load_initial_data()
        im.load_items() # Reload
        
    pet = PetWindow()
    pet.show()

    # 关键：添加一个定时器让 Python解释器 有机会运行，从而能捕获信号
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    # 初始化托盘图标
    tray = SystemTray(pet, app)
    pet.set_tray(tray)
    
    # 3. 设置清理逻辑
    def signal_handler(signum, frame):
        logger.info(f"用户强制退出 ({signal.Signals(signum).name})")
        pet.close() # 触发保存
        app.quit() # 退出 Qt 事件循环
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # 正常运行
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
