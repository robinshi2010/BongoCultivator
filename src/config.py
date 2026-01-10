"""
游戏配置常量
"""

# 境界名称列表
LAYERS = [
    "炼气期", "筑基期", "金丹期", "元婴期", "化神期", "炼虚期", "合体期", "大乘期", "渡劫期", "飞升"
]

# 各境界所需经验值 (Based on Plan 4 & 6)
EXP_TABLE = [
    30000,       # 0: 炼气 (Target: ~1h)
    120000,      # 1: 筑基 (Target: ~3h)
    800000,      # 2: 金丹 (Target: ~24h)
    2500000,     # 3: 元婴
    8000000,     # 4: 化神
    20000000,    # 5: 炼虚
    50000000,    # 6: 合体
    100000000,   # 7: 大乘
    200000000,   # 8: 渡劫
    999999999    # 9: 飞升 (Max)
]

# ===== 游戏机制配置 =====

# 事件触发间隔 (秒) - 每隔多久触发一次随机事件
EVENT_INTERVAL_SECONDS = 300  # 5分钟

# 坊市自动刷新间隔 (秒)
MARKET_REFRESH_INTERVAL = 15 * 60  # 15分钟 (Plan 48: 从8小时缩短)

# 每日勤勉奖励阈值 (操作数)
DAILY_REWARD_THRESHOLD = 2000
DAILY_REWARD_SMALL = 100   # 普通奖励
DAILY_REWARD_BIG = 500     # 大奖 (超过10000操作)
DAILY_REWARD_BIG_THRESHOLD = 10000

# 掉落物品的最小间隔 (秒)
DROP_COOLDOWN_SECONDS = 5.0
