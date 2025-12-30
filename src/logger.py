import sys
import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    """
    配置全局日志系统，包括控制台输出和文件记录。
    同时设置全局异常捕获钩子。
    """
    # 1. 确定日志目录
    from src.utils.path_helper import get_user_data_dir
    log_dir = os.path.join(get_user_data_dir(), 'logs')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. 定义日志文件名
    log_file = os.path.join(log_dir, 'app.log')

    # 3. 配置 Logger
    logger = logging.getLogger('BongoCultivator')
    logger.setLevel(logging.DEBUG)

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    # 4. Formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 5. File Handler (Rotating)
    # 限制单个文件 5MB，最多备份 3 个
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 6. Console Handler (方便调试)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 7. 设置全局异常 Hook
    def handle_exception(exc_type, exc_value, exc_traceback):
        # 忽略 KeyboardInterrupt (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical("未捕获的异常 (Uncaught exception):", exc_info=(exc_type, exc_value, exc_traceback))
        
        # 将 traceback 写入单独的 crash 文件方便快速查看 (可选)
        # crash_file = os.path.join(log_dir, f'crash_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        # with open(crash_file, 'w', encoding='utf-8') as f:
        #     traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        
        # 也可以在这里弹窗提示用户发送错误报告
        
    sys.excepthook = handle_exception
    
    logger.info("日志系统已启动 (Log system initialized).")
    return logger

# 预初始化, 只要 import logger 就会生效
logger = setup_logging()
