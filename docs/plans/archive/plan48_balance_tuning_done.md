# Plan 48: 游戏平衡性调整 (Game Balance Tuning)

## 问题背景 (Problem Context)

根据游戏测试反馈，发现以下几个平衡性问题需要调整：

1. **挂机收益过低**: IDLE 状态每秒只获得 1 修为，相比其他状态过于微薄
2. **坊市刷新间隔过长**: 当前 8 小时刷新一次，玩家难以及时购买所需物品
3. **渡劫期心魔积累过快**: `evt_t8_c1` 事件触发时直接增加 20 心魔，对渡劫期玩家过于惩罚
4. **丹药配方重复**: `身外化身丹`(水属性回复丹) 和 `幽冥锻体丹`(体魄丹) 使用完全相同的材料，缺乏差异性

## 目标 (Goals)

1. ✅ 提升挂机基础收益，增加挂机专属的正面事件
2. ✅ 缩短坊市刷新间隔至 15 分钟
3. ✅ 降低渡劫期事件的心魔惩罚
4. ✅ 重新设计两款丹药的配方，体现差异性

---

## 详细设计 (Technical Design)

### 1. 提升挂机收益

#### 1.1 修改基础修为获取

**文件**: `src/cultivator.py`

将 IDLE 状态的基础修为从 `1` 提升到 `3`：

```python
# Before
if kb_apm < 30 and mouse_apm < 30:
    # IDLE
    base_exp = 1

# After  
if kb_apm < 30 and mouse_apm < 30:
    # IDLE - 闭关修炼
    base_exp = 3  # 提升挂机收益
```

#### 1.2 新增挂机专属正面事件

**文件**: `src/data/events.json`

添加新的 IDLE 状态专属事件：

```json
[
    {
        "id": "evt_idle_meditation_1",
        "title": "入定感悟",
        "type": "Common",
        "text": "在闭关中，你进入了深层入定状态，修为精进。",
        "weight": 80,
        "min_layer": 0,
        "max_layer": 9,
        "state": "IDLE",
        "effects": {
            "exp": [100, 500],
            "mind": -5
        }
    },
    {
        "id": "evt_idle_meditation_2",
        "title": "天人合一",
        "type": "Uncommon",
        "text": "你的呼吸与天地灵气同频，修炼效率大幅提升。",
        "weight": 30,
        "min_layer": 1,
        "max_layer": 9,
        "state": "IDLE",
        "effects": {
            "exp": [500, 2000]
        }
    },
    {
        "id": "evt_idle_enlightenment",
        "title": "醍醐灌顶",
        "type": "Rare",
        "text": "冥冥中，你似乎触摸到了大道的边缘，修为大涨！",
        "weight": 10,
        "min_layer": 2,
        "max_layer": 9,
        "state": "IDLE",
        "effects": {
            "exp": [2000, 10000],
            "mind": -10
        }
    }
]
```

### 2. 缩短坊市刷新间隔

**文件**: `src/config.py`

```python
# Before
MARKET_REFRESH_INTERVAL = 8 * 3600  # 8小时

# After
MARKET_REFRESH_INTERVAL = 15 * 60  # 15分钟
```

### 3. 平衡渡劫期心魔惩罚

**文件**: `src/data/events.json`

修改 `evt_t8_c1` 事件：

```json
// Before
{
    "id": "evt_t8_c1",
    "title": "天道窥视",
    "effects": {
        "mind": 20  // 太高了！
    }
}

// After
{
    "id": "evt_t8_c1",
    "title": "天道窥视",
    "effects": {
        "mind": 5,   // 降低心魔增加
        "exp": 8000  // 补偿一些经验
    }
}
```

同时添加渡劫期专属的正面事件来平衡：

```json
{
    "id": "evt_t8_blessing",
    "title": "天道庇佑",
    "type": "Common",
    "text": "或许是认可了你的努力，天道之眼中透出一丝温和。",
    "weight": 80,
    "min_layer": 8,
    "max_layer": 8,
    "effects": {
        "exp": 20000,
        "mind": -10
    }
}
```

### 4. 重新设计丹药配方

**文件**: `src/data/items.json`

#### 4.1 身外化身丹 (水属性灵液回复丹)

当前配方: `herb_soul_restore x1 + water_nether x2`

新配方设计 (强调水属性/分身/元婴类材料):
```json
{
    "id": "pill_avatar",
    "name": "身外化身丹",
    "recipe": {
        "water_nether": 2,
        "herb_dragon_1": 1,
        "ore_void_stone": 1
    }
}
```
- **黄泉鬼水 x2**: 提供阴性能量
- **龙纹草 x1**: 增强神识分化能力
- **虚空石 x1**: 提供空间属性，支撑化身存在

#### 4.2 幽冥锻体丹 (体魄强化丹)

当前配方: `water_nether x2 + herb_soul_restore x1`

新配方设计 (强调淬体/阳刚/肉身强化类材料):
```json
{
    "id": "pill_body_nether",
    "name": "幽冥锻体丹",
    "recipe": {
        "water_nether": 1,
        "bone_kirin_arm": 1,
        "ore_star_sand": 2
    }
}
```
- **黄泉鬼水 x1**: 提供阴冷淬炼
- **麒麟臂骨 x1**: 上古圣兽骨骼，增强筋骨
- **星辰砂 x2**: 天外陨石精华，淬炼肉身

---

## 实施步骤 (Implementation Steps)

### ✅ 步骤 1: 修改配置常量
- 修改 `src/config.py` 中的 `MARKET_REFRESH_INTERVAL`

### ✅ 步骤 2: 调整挂机基础收益
- 修改 `src/cultivator.py` 中 IDLE 状态的 `base_exp`

### ✅ 步骤 3: 更新事件数据
- 修改 `src/data/events.json` 中 `evt_t8_c1` 的心魔效果
- 添加新的挂机专属事件
- 添加渡劫期平衡事件

### ✅ 步骤 4: 更新丹药配方
- 修改 `src/data/items.json` 中两款丹药的 recipe

### 步骤 5: 同步数据库
- 运行 `python tools/import_all_data.py` 刷新数据库

---

## 文件变更清单 (Files Changed)

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `src/config.py` | 修改 | 坊市刷新间隔改为 15 分钟 |
| `src/cultivator.py` | 修改 | IDLE 基础修为从 1 提升到 3 |
| `src/data/events.json` | 修改 | 调整 T8 事件，新增挂机事件 |
| `src/data/items.json` | 修改 | 重新设计两款丹药配方 |

---

## 数值对比 (Before/After)

| 指标 | 调整前 | 调整后 | 说明 |
|------|--------|--------|------|
| IDLE 基础修为/秒 | 1 | 3 | +200% |
| 坊市刷新间隔 | 8小时 | 15分钟 | 大幅缩短 |
| T8 天道窥视心魔 | +20 | +5 | -75% |
| T8 天道窥视经验 | 0 | +8000 | 新增补偿 |

---

**预计工作量**: 30 分钟
**优先级**: 中 (用户体验优化)

---

## ✅ 完成状态

- **完成时间**: 2026-01-10 23:42
- **实现内容**:
  - ✅ 坊市刷新间隔从 8 小时缩短至 15 分钟
  - ✅ IDLE 状态基础修为从 1 提升到 3 (+200%)
  - ✅ 渡劫期「天道窥视」心魔从 +20 降至 +5，新增经验补偿 +8000
  - ✅ 新增渡劫期「天道庇佑」正面事件 (经验+20000, 心魔-10)
  - ✅ 新增 4 个 IDLE 专属事件 (入定感悟、天人合一、醐醐灌顶、心如止水)
  - ✅ 重新设计「身外化身丹」配方 (黄泉鬼水x2 + 龙纹草x1 + 虚空石x1)
  - ✅ 重新设计「幽冥锻体丹」配方 (黄泉鬼水x1 + 麒麟臂骨x1 + 星辰砂x2)
  - ✅ 数据库同步完成 (66 events, 121 items, 42 recipes)
- **测试验证**: 模块加载验证通过 ✅
