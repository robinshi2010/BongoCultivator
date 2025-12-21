import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.pet_window import PetWindow
from src.logger import logger  # 初始化日志

import signal

def main():
    logger.info("启动应用程序...")
    app = QApplication(sys.argv)
    
    # 可以在这里做一些全局配置，比如样式表
    
    pet = PetWindow()
    pet.show()

    # 关键：添加一个定时器让 Python解释器 有机会运行，从而能捕获信号
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    
    # 使用 signal 处理 Ctrl+C
    def signal_handler(sig, frame):
        logger.info("用户强制退出 (SIGINT)")
        pet.close() # 保存数据
        QApplication.quit() # 退出 Qt 事件循环
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # 正常运行
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
