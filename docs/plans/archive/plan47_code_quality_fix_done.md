# Plan 47: 代码质量审查与修复 (Code Quality Review & Fixes)

## 问题背景 (Problem Context)

对项目进行全面的代码审查时，发现了多处严重的代码质量问题：

1. **代码重复 (Duplicate Code)**: 多处存在重复的语句，导致逻辑错误
2. **死代码 (Dead Code)**: 废弃的方法定义未清理，造成混淆
3. **魔法数字 (Magic Numbers)**: 硬编码的数值散布在代码中，难以维护
4. **依赖缺失**: `requirements.txt` 缺少部分依赖声明
5. **工具目录臃肿**: 一次性脚本与常用工具混杂

## 发现的问题清单

### 🔴 P0 严重问题

| 位置 | 问题描述 | 影响 |
|------|----------|------|
| `cultivator.py:637-639` | `gain_exp()` 调用重复 | **离线经验翻倍 Bug** |
| `cultivator.py:346-347` | `msg = ...` 赋值重复 | 代码冗余 |
| `cultivator.py:362-363` | `msg = ...` 赋值重复 | 代码冗余 |
| `cultivator.py:593-596` | `elif` 分支重复 | 逻辑冗余 |
| `cultivator.py:797-798` | `talent_points += 1` 重复 | 秘籍奖励翻倍 |

### 🟠 P1 中等问题

| 位置 | 问题描述 |
|------|----------|
| `cultivator.py:210-264` | 旧的 `save_data(filepath)` 和 `load_data(filepath)` 死代码 |
| `main.py:1,8` | 重复的 `import sys` |
| `main.py:16,34` | 重复的 `from src.services.data_loader import DataLoader` |
| `src/event_manager.py` | 废弃的 EventManager 类（已被 EventEngine 替代） |

### 🟡 P2/P3 轻微问题

| 问题 | 涉及文件 |
|------|----------|
| 魔法数字散布 | `cultivator.py` 多处 |
| requirements.txt 不完整 | 缺少 matplotlib, Pillow |
| .gitignore 备份文件规则缺失 | `.gitignore` |
| 工具目录缺少说明 | `tools/` |
| 无意义注释 | `cultivator.py` |

## 修复方案 (Solution)

### ✅ 步骤 1：修复代码重复问题

**文件**: `src/cultivator.py`

删除以下重复代码：
```python
# Line 346-347: 删除重复的 msg 赋值
msg = f"雷劫洗礼，金光护体！\n晋升【{self.current_layer}】\n体魄+2，天赋点+1"
# msg = f"..."  <- 删除此行

# Line 362-363: 同上
# Line 593-596: 删除重复的 elif 分支
# Line 637-639: 删除重复的 gain_exp() 调用  <- 严重 Bug！
# Line 797-798: 删除重复的 talent_points += 1
```

### ✅ 步骤 2：删除死代码

**文件**: `src/cultivator.py`

删除旧的 JSON 文件保存/加载方法（第 210-264 行），这些已被 SQLite 版本覆盖。

同时删除无意义的占位注释：
```python
# ... (properties methods) ...  <- 删除
# ... (existing methods) ...    <- 删除
```

### ✅ 步骤 3：清理重复导入

**文件**: `main.py`

```python
# Before:
import sys
from PyQt6.QtWidgets import QApplication
...
import signal
import sys  # <- 删除重复

# After:
import sys
import signal
from PyQt6.QtWidgets import QApplication
...
```

### ✅ 步骤 4：删除废弃模块

删除文件：`src/event_manager.py`

该类已被 `src/services/event_engine.py` 完全替代，且无任何地方导入使用。

### ✅ 步骤 5：提取魔法数字到配置

**文件**: `src/config.py`

新增配置常量：
```python
# 事件触发间隔 (秒)
EVENT_INTERVAL_SECONDS = 300  # 5分钟

# 坊市自动刷新间隔 (秒)
MARKET_REFRESH_INTERVAL = 8 * 3600  # 8小时

# 每日勤勉奖励阈值 (操作数)
DAILY_REWARD_THRESHOLD = 2000
DAILY_REWARD_SMALL = 100
DAILY_REWARD_BIG = 500
DAILY_REWARD_BIG_THRESHOLD = 10000

# 掉落物品的最小间隔 (秒)
DROP_COOLDOWN_SECONDS = 5.0
```

**文件**: `src/cultivator.py`

更新导入并使用新常量替换硬编码值。

### ✅ 步骤 6：完善依赖声明

**文件**: `requirements.txt`

```txt
PyQt6>=6.4.0
pynput>=1.7.6
sqlmodel>=0.0.14
matplotlib>=3.7.0   # 新增
Pillow>=9.5.0       # 新增
```

### ✅ 步骤 7：更新 .gitignore

**文件**: `.gitignore`

添加通用备份文件排除规则：
```gitignore
# Backup files
*.bak
*.json.bak
```

### ✅ 步骤 8：整理工具目录

1. 创建 `tools/archive/` 子目录
2. 将一次性脚本 (`fix_*.py`, `update_*.py` 等) 移动到归档目录
3. 创建 `tools/README.md` 说明文档

## 文件变更清单 (Files Changed)

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `src/cultivator.py` | 修改 | 删除重复代码、死代码，使用配置常量 |
| `src/config.py` | 修改 | 新增游戏机制配置常量 |
| `main.py` | 修改 | 清理重复导入 |
| `requirements.txt` | 修改 | 添加缺失依赖 |
| `.gitignore` | 修改 | 添加备份文件规则 |
| `src/event_manager.py` | **删除** | 废弃的死代码 |
| `tools/README.md` | **新增** | 工具目录说明 |
| `tools/archive/` | **新增** | 归档一次性脚本 |
| `docs/memory.md` | 修改 | 更新时间戳 |

## 验证测试 (Verification)

```bash
# 验证模块导入
python3 -c "from src.cultivator import Cultivator; from src.config import *; print('✅ 模块导入成功')"

# 验证实例化
python3 -c "from src.cultivator import Cultivator; c = Cultivator(); print(f'✅ Cultivator 初始化成功, 事件间隔: {c.event_interval}s')"

# 验证 main.py
python3 -c "import main; print('✅ main.py 导入成功')"
```

---

## ✅ 完成状态

- **完成时间**: 2026-01-10 23:33
- **实现内容**:
  - ✅ 修复 5 处代码重复问题（包括离线经验翻倍 Bug）
  - ✅ 删除 58 行死代码（旧的 save_data/load_data 方法）
  - ✅ 清理 main.py 中的重复导入
  - ✅ 删除废弃的 EventManager 模块
  - ✅ 将魔法数字提取到 config.py（6 个新常量）
  - ✅ 完善 requirements.txt 依赖声明
  - ✅ 更新 .gitignore 备份文件规则
  - ✅ 整理 tools 目录结构并添加说明文档
- **测试验证**: 所有模块导入验证通过 ✅
