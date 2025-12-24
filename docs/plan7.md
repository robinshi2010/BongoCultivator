# Plan 7: 物品系统重构与数据库迁移 (Item System Overhaul & SQLite Migration)

## 1. 物品与丹药体系重构

当前物品系统较为简陋，需按照修仙境界进行标准化重构。
每个大境界 (Tier 0 - Tier 8) 将包含专属的灵物与丹药体系。

### 1.1 设计原则
- **灵物 (Spirit Items)**: 天地生成的原材料。可以直接吞服，但效果微弱且可能伴有副作用 (如增加少量心魔)。
- **丹药 (Pills)**: 由灵物炼制而成。效果显著，包含增加修为、突破境界、永久属性提升、临时Buff等。
- **配方 (Recipes)**: 每个境界至少包含 **5种** 核心丹药。

### 1.2 境界物品规划 (示例: 炼气期 Tier 0)
*注：具体数值需参考 Plan 4 & 6 的平衡标准。*

| 类型 | ID | 名称 | 描述/效果 | 来源 |
| :--- | :--- | :--- | :--- | :--- |
| **灵物** | `herb_spirit_0` | **下品灵草** | 吞服:+10修为 | 挂机/历练 |
| **灵物** | `fruit_essence_0` | **聚元果** | 吞服:+20修为 | 历练(低概率) |
| **灵物** | `ore_iron_0` | **玄铁** | 炼器/炼丹辅材 | 键盘高频操作 |
| **丹药** | `pill_exp_0` | **聚气丹** | +100修为 | 灵草x3 + 辅材 |
| **丹药** | `pill_heal_0` | **回春丹** | 恢复状态/减少心魔 | 聚元果x1 + 灵草x1 |
| **丹药** | `pill_buff_speed` | **神行散** | 掉落率+20% (30m) | 灵草x5 |
| **丹药** | `pill_buff_idle` | **辟谷丹** | 挂机收益+10% (1h) | 聚元果x2 |
| **丹药** | `pill_break_0` | **筑基丹** | 突破至筑基期 (成功率↑) | 稀有主材 + 大量辅材 |

*(后续筑基、金丹、元婴等境界以此类推，需设计 9 套物品)*

---

## 2. 数据库迁移 (SQLite)

将目前的 JSON 存储 (`items.json`, `save_data.json`) 全面迁移至 `user_data.db`。

### 2.1 数据库表结构设计

#### A. 游戏数据表 (Game Data) - 静态配置
*建议：为了便于热更和调整，这部分数据既若保留 JSON 加载也可以，但为了响应“改为写入sqlite”的需求，我们将把配置导入数据库。*

```sql
-- 物品定义表
CREATE TABLE item_definitions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,       -- material, consumable, equipment
    tier INTEGER,    -- 对应境界层级
    description TEXT,
    price INTEGER,
    effect_json TEXT -- JSON 字符串存储具体效果
);

-- 配方表
CREATE TABLE recipes (
    result_item_id TEXT PRIMARY KEY,
    ingredients_json TEXT, -- {"item_a": 2, "item_b": 1}
    craft_time INTEGER,    -- 炼制秒数
    success_rate REAL      -- 初始成功率
);
```

#### B. 用户数据表 (User Data) - 动态存档

```sql
-- 角色状态表 (单行记录)
CREATE TABLE player_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    layer_index INTEGER DEFAULT 0, -- 境界索引
    current_exp INTEGER DEFAULT 0,
    money INTEGER DEFAULT 0,
    
    -- 核心属性
    start_body INTEGER DEFAULT 10,  -- 体魄
    stat_mind INTEGER DEFAULT 0,    -- 心魔
    stat_luck INTEGER DEFAULT 0,    -- 气运 (好感度)
    
    talent_points INTEGER DEFAULT 0,
    talent_json TEXT,              -- 天赋树数据
    
    last_save_time INTEGER,
    last_login_time INTEGER
);

-- 背包表
CREATE TABLE player_inventory (
    item_id TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0,
    FOREIGN KEY(item_id) REFERENCES item_definitions(id)
);

-- 成就/事件记录 (可选)
CREATE TABLE player_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    event_type TEXT,
    message TEXT
);
```

### 2.2 迁移策略
1.  **Init**: 程序启动时，检查数据库表是否存在。
2.  **Import**: 如果是首次运行或版本更新，读取 `src/data/items.json` 并刷新到 `item_definitions` 表。
3.  **Load**: 替代原有的 `cultivator.load_data()`，从 SQLite 读取玩家状态。
4.  **Save**: 替代原有的 `cultivator.save_data()`，将内存数据写入 SQLite。

---

## 3. 数据重置与管理

### 3.1 删档/重置 (Hard Reset)
为了方便调试或“转世重修”，提供重置接口。

**操作方式**:
调用 `BaseCultivator.reset_to_beginning()` (需新增方法)。

**逻辑**:
```python
def reset_to_beginning(self):
    # 1. 事务开始
    # 2. DELETE FROM player_inventory;
    # 3. UPDATE player_status SET 
    #       layer_index=0, current_exp=0, money=0, 
    #       stat_mind=0, stat_luck=0 ...
    #       WHERE id=1;
    # 4. 提交并刷新内存对象
    # 5. UI 提示 "转世成功"
```

### 3.2 调试指令
在 `Plan 5` 的秘籍系统中添加指令：
- `reborn`: 触发重置逻辑，回到炼气期 0 XP。

---

## 4. 执行步骤

1.  **数据梳理**: 编写脚本生成 9 个境界的物品数据 (可先用脚本生成占位数据，后续手动精修文案)。
2.  **后端改造**: 修改 `src/database.py`，实现上述表结构。
3.  **逻辑对接**: 修改 `src/cultivator.py` 和 `src/item_manager.py` 对接数据库。
4.  **验证**: 确保存档能正常读写，物品能正常显示。

---
**Status**: Completed

## 完成情况记录 (Completion Log)
*Date: 2025-12-24*

### 1. 数据库构建
- 在 `src/database.py` 中实现了完整的 SQLite Schema:
    - `item_definitions`: 物品静态数据
    - `recipes`: 配方数据
    - `player_status`: 用户存档 (ID=1)
    - `player_inventory`: 用户背包
    - `player_events`: 事件日志
- 实现了 `_init_db` 自动初始化逻辑。

### 2. 物品系统重构 (Item System v2)
- 编写了 `tools_generate_items.py`，程序化生成了从炼气期(Tier 0)到渡劫期(Tier 8)的 9 套标准物品数据。
- 包含：灵草(common)、元果(rare)、妖丹(material)、以及 5 种标准丹药(经验/回复/Buff/突破)。
- 修改 `src/item_manager.py`:
    - 启动时自动检查 DB，若为空则从 `items_v2.json` 导入数据。
    - 内存中改为从 DB 加载数据，支持 0-8 动态层级。

### 3. 存档迁移与逻辑更新
- 修改 `src/cultivator.py`:
    - `load_data`: 优先读取 SQLite，若无数据则自动读取旧 `save_data.json` 并迁移入库，旧文件备份为 `.bak`。
    - `save_data`: 全面改为写入 SQLite。
    - `reset_to_beginning`: 实现了重置/转世逻辑。
    - 整合了 Plan 4 的 `EXP_TABLE` 和 Plan 6 的动态坊市掉落逻辑。

### 4. 验证
- 通过 `tools_verify_db.py` 验证了物品导入的正确性 (71种物品)。
- 通过 `tools_verify_cultivator.py` 验证了存档迁移、读取和新坊市刷新逻辑的正确性。
