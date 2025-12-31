# Plan 28: 核心代码重构与 ORM 迁移 (Refactor & SQLModel)

## 📌 目标 (Obective)

本计划旨在解决代码审查 (Code Review) 中发现的关键 Bug、架构紧耦合以及代码冗余问题。核心手段是引入 **SQLModel** (ORM)，将业务逻辑与底层数据库操作解耦，同时修复潜在的逻辑错误，提升代码的可维护性和健壮性。

---

## 🛠️ 执行步骤 (Implementation Steps)

### Phase 1: 关键修复与清理 (Hotfix & Cleanup)
- [ ] **修复 EventEngine Bug**: 修正 `src/services/event_engine.py` 中 `trigger_event` 方法因 `return` 语句位置错误导致 `_record_history` 无法执行的问题。
- [ ] **清理废弃代码**: 移除 `Cultivator.load_data` 中旧版 JSON 存读档的大量冗余兼容逻辑，仅保留 SQL 加载，保持代码整洁。

### Phase 2: 引入 SQLModel (ORM Integration)
- [ ] **添加依赖**: 更新 `requirements.txt`，加入 `sqlmodel`。
- [ ] **建立模型层 (`src/models/`)**: 创建新的目录和文件，定义数据库表结构对应的 Python 类：
    - `src/models/player_status.py`: 玩家基础属性 (Layer, Exp, Attributes)。
    - `src/models/inventory.py`: 物品系统 (Items, Market)。
    - `src/models/logs.py`: 统计日志 (Activity, Events)。
    - `src/models/system.py`: 系统元数据。
- [ ] **重构数据库管理 (`src/database.py`)**: 
    - 替换原生 `sqlite3` 为 SQLModel 的 `Session` 和 `Engine`。
    - 确保新 ORM 兼容旧的表结构 (无需复杂的 Migration，如果不破坏结构的话；或者使用 `SQLModel.metadata.create_all` 自动处理增量)。

### Phase 3: 业务逻辑层重构 (Service Refactor)
- [ ] **重构 `Cultivator` 数据存取**:
    - 将 `save_data` / `load_data` 中的 SQL 拼接逻辑完全替换为 ORM 操作。
    - 实现数据的事务性保存。
- [ ] **重构 `EventEngine` 数据交互**:
    - 使用 ORM 查询 `EventHistory` 和 `EventDefinition`。
- [ ] **重构 `ActivityRecorder`**:
    - 使用 ORM 写入每分钟的操作日志。

### Phase 4: 配置抽离与优化 (Config & Optimization)
- [ ] **配置中心化**: 将 `EXP_TABLE`, `LAYERS` 等硬编码在 `Cultivator` 类的常量抽离到独立文件 `src/config.py`。
- [ ] **God Class 拆分 (可选)**: 评估 `PetWindow` 的复杂度，如果时间允许，将部分 UI 布局计算逻辑抽离。

---

## ✅ 验收标准 (Acceptance Criteria)
1.  所有原有功能 (存档、物品、事件触发) 正常工作，无回归 Bug。
2.  `src/cultivator.py` 中不再包含任何 SQL 语句。
3.  `EventEngine` 的 `unique` 属性事件在触发一次后，确实被记录且不会再次触发。
4.  代码结构清晰，Models 定义明确。
