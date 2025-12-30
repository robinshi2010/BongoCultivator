import sys
import os

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径。
    支持 Dev 环境和 PyInstaller 打包环境 (_MEIPASS)。
    :param relative_path: 相对路径 (例如 'assets/icon.png' 或 'src/data/items.json')
    :return: 绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
    else:
        # 开发环境: 项目根目录
        # 假设此文件在 src/utils/path_helper.py -> ../.. 是根目录
        # 但这也取决于 relative_path 是相对于谁。
        # 通常我们约定 relative_path 是相对于项目根目录 (bongo/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(os.path.dirname(current_dir))
        
    return os.path.join(base_path, relative_path)

import platform
from pathlib import Path

def get_legacy_data_dir():
    """获取旧版数据目录 (用于迁移)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # src/utils/path_helper.py -> src/utils -> src -> root
        return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

def get_user_data_dir():
    """
    获取标准化的用户数据存储目录。
    macOS: ~/Library/Application Support/BongoCultivation
    Windows: %LOCALAPPDATA%/BongoCultivation
    """
    app_name = "BongoCultivator"
    system = platform.system()
    
    if system == "Windows":
        base_path = Path(os.getenv('LOCALAPPDATA')) / app_name
    elif system == "Darwin":
        base_path = Path.home() / "Library" / "Application Support" / app_name
    else:
        base_path = Path.home() / ".local" / "share" / app_name
        
    try:
        base_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating data dir {base_path}: {e}")
        # Fallback to tmp or legacy if permission denied?
        return get_legacy_data_dir()
        
    return str(base_path)
