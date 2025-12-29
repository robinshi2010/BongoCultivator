# Plan 22: 数据持久化与存档迁移 (Data Persistence & Migration)

## 问题背景 (Problem Context)
当前游戏的存档文件 (`user_data.db` 和 `save_data.json`) 默认存储在**应用程序所在目录** (Executable Directory)。
- **开发环境**: 项目根目录。
- **打包环境**: `.app` 包或者 `.exe` 同级目录。

当用户更新游戏时，通常会下载新的安装包并解压，这往往意味着：
1.  **覆盖安装**: 旧文件夹被覆盖，如果旧存档在其中，可能会被清理或丢失。
2.  **新文件夹运行**: 用户在新的文件夹运行新版游戏，读取的是当前新文件夹下的（空）数据，导致“存档丢失”的假象。

## 目标 (Goals)
实现标准化的数据持久化存储，将存档文件与程序文件分离。
无论用户如何删除、移动或更新应用程序（`.app`/`.exe`），存档都应安全保存在系统的特定用户目录下。

## 解决方案 (Solution)

### 1. 确定标准存储路径
使用操作系统推荐的用户数据目录：
- **macOS**: `~/Library/Application Support/BongoCultivation/`
- **Windows**: `C:\Users\<User>\AppData\Local\BongoCultivation\` (通常通过 `%LOCALAPPDATA%` 获取)

### 2. 自动迁移机制 (Migration Logic)
为了兼容老用户，在启动时必须检查：
1.  **新目录**下是否有存档？
    - **有**: 直接使用 (正常流程)。
    - **无**: 检查**旧目录** (程序同级目录) 是否有存档？
        - **有**: 将旧存档**复制**到新目录，并继续使用新目录。
        - **无**: 初始化新存档 (新用户)。

## 实施步骤 (Implementation Steps)

### 步骤 1: 修改 `src/utils/path_helper.py`
引入 `platform`, `pathlib` 等库，重写 `get_user_data_dir` 函数。

```python
import platform
from pathlib import Path

def get_user_data_dir():
    app_name = "BongoCultivation"
    system = platform.system()
    
    if system == "Windows":
        base_path = Path(os.getenv('LOCALAPPDATA')) / app_name
    elif system == "Darwin":
        base_path = Path.home() / "Library" / "Application Support" / app_name
    else:
        # Linux/Other: ~/.local/share/BongoCultivation
        base_path = Path.home() / ".local" / "share" / app_name
        
    # 确保目录存在
    base_path.mkdir(parents=True, exist_ok=True)
    return str(base_path)
```

**保留旧路径获取方法** (用于迁移 Check):
```python
def get_legacy_data_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir)) # src/utils/../.. -> root
```

### 步骤 2: 实现数据迁移逻辑
在 `src/database.py` 初始化或 `main.py` 启动早期调用迁移。推荐在 `main.py` 最开始调用。

并在 `src/utils/data_migration.py` (新建) 中实现：

```python
def check_and_migrate_data():
    new_dir = get_user_data_dir()
    old_dir = get_legacy_data_dir()
    
    files_to_migrate = ["user_data.db", "save_data.json"]
    
    for filename in files_to_migrate:
        new_path = os.path.join(new_dir, filename)
        old_path = os.path.join(old_dir, filename)
        
        # 如果新文件不存在，且旧文件存在 -> 复制
        if not os.path.exists(new_path) and os.path.exists(old_path):
            logger.info(f"正在迁移数据: {filename} 从 {old_dir} -> {new_dir}")
            try:
                shutil.copy2(old_path, new_path)
                logger.info("迁移成功！")
            except Exception as e:
                logger.error(f"迁移失败: {e}")
```

### 步骤 3: 更新资源加载
确保 `src/database.py` 和其他使用 `get_user_data_dir` 的地方不再硬编码路径，而是调用新的函数。
(现有代码应该已经是调用的 `get_user_data_dir`，所以只要修改函数实现即可平滑切换)。

## 验证计划 (Verification)
1.  **前置准备**: 在项目根目录生成一个有数据的 `user_data.db` (旧模式)。
2.  **执行代码更改**: 应用新逻辑。
3.  **运行程序**:
    - 检查日志，确认打印了“正在迁移数据...”。
    - 检查 `~/Library/Application Support/BongoCultivation/` 目录下是否出现了 `.db` 文件。
    - 游戏中读取到了之前的数据，而非空档。
4.  **再次运行**: 确认直接读取新目录，不再迁移。

