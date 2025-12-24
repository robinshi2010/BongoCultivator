import random
from src.logger import logger
from src.item_manager import ItemManager
from src.event_manager import EventManager

class Cultivator:
    LAYERS = [
        "炼气期", "筑基期", "金丹期", "元婴期", "化神期", "炼虚期", "合体期", "大乘期", "渡劫期"
    ]
    
    # Based on Plan 4 & 6 (Standardized 9 Tiers)
    EXP_TABLE = [
        200000,      # 0: 炼气
        1400000,     # 1: 筑基
        6000000,     # 2: 金丹
        6000000,     # 3: 元婴
        9000000,     # 4: 化神
        13500000,    # 5: 炼虚
        20250000,    # 6: 合体
        30375000,    # 7: 大乘
        999999999    # 8: 渡劫 (Max)
    ]
    
    def __init__(self):
        self.exp = 0
        self.layer_index = 0
        self.money = 0 # 灵石
        self.inventory = {} # 物品栏 {id: count}
        self.events = [] # 事件日志
        
        # 核心属性
        self.mind = 0      # 心魔 (0-100)，越高修练越慢
        self.body = 10     # 体魄 (基础10)，影响渡劫成功率
        self.affection = 0 # 好感度 (0-100)，影响材料掉率
        
        # 坊市数据
        self.market_goods = [] # [{id, price, discount}]
        self.last_market_refresh = 0
        
        # 事件系统
        self.last_event_time = 0 
        self.event_interval = 300 # 300秒(5分钟)触发一次随机事件 (测试可改为30)
        
        # 初始化 ItemManager 和 EventManager
        self.item_manager = ItemManager()
        self.event_manager = EventManager()
        
        # 天赋系统
        self.talent_points = 0
        self.talents = {
            "exp": 0,  # 修炼天赋: +5% 经验获取
            "drop": 0  # 寻宝天赋: +5% 掉落概率
        }
        
        # 每日任务相关
        self.daily_reward_claimed = None # 记录上次领奖日期 'YYYY-MM-DD'
        
    # ... (properties methods) ...

    def modify_stat(self, stat, value):
        if stat == "mind":
            self.mind = max(0, min(100, self.mind + value))
        elif stat == "body":
            self.body = max(1, self.body + value) # 体魄无上限
        elif stat == "affection":
            self.affection = max(0, min(100, self.affection + value))
        elif stat == "reset_talent":
            self.reset_talents()
            
    def reset_talents(self):
        total = sum(self.talents.values())
        self.talents["exp"] = 0
        self.talents["drop"] = 0
        self.talent_points += total
        logger.info(f"洗髓成功! 返还 {total} 天赋点")

    def upgrade_talent(self, talent_type):
        if self.talent_points > 0 and talent_type in self.talents:
            self.talents[talent_type] += 1
            self.talent_points -= 1
            return True
        return False

    def refresh_market(self):
        """刷新坊市商品 (每天一次 or 手动)"""
        import time
        self.last_market_refresh = time.time()
        self.market_goods = []
        
        # 随机生成 6 个商品
        # 逻辑：3个材料，2个消耗品，1个珍稀(低概率)
        # 随机生成 6 个商品
        current_tier = min(self.layer_index, 8)
        
        for _ in range(6):
            # 随机决定类型
            roll = random.random()
            if roll < 0.6: # 60% 材料
                item_id = self.item_manager.get_random_material(current_tier)
            else: # 40% 丹药
                candidates = self.item_manager.tier_lists.get(current_tier, {}).get("pills", [])
                item_id = random.choice(candidates) if candidates else None
                
            if item_id:
                info = self.item_manager.get_item(item_id)
                base_price = info.get("price", 100)
                
                # 随机折扣 (0.8 ~ 1.25)
                discount = round(random.uniform(0.8, 1.2), 2)
                final_price = int(base_price * discount)
                
                self.market_goods.append({
                    "id": item_id,
                    "price": final_price,
                    "discount": discount
                })
        
        logger.info("坊市商品已刷新")

    def check_daily_refresh(self):
        """检查是否需要每日自动刷新"""
        import time
        # 简单判断: 超过24小时刷新? 或者每天0点?
        # 这里用简单的时间间隔: 8小时刷新一次
        if time.time() - self.last_market_refresh > 8 * 3600:
            self.refresh_market()

    def claim_daily_work_reward(self, total_actions):
        """
        尝试领取每日“勤勉”奖励
        :param total_actions: 今日总操作数 (keys + clicks)
        :return: (bool success, str message)
        """
        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        if self.daily_reward_claimed == today_str:
            return False, "今日奖励已领取，明日再来吧！"
            
        # 阈值设定: 比如 2000 操作算“勤勉”
        threshold = 2000 
        if total_actions < threshold:
            return False, f"功力未够！今日仅 {total_actions} 操作，需 {threshold} 方可领赏。"
            
        # 发放奖励
        reward_money = 100
        # 额外：如果操作非常多 (>10000)，给大奖
        is_big_win = total_actions > 10000
        if is_big_win:
            reward_money = 500
            
        self.money += reward_money
        self.daily_reward_claimed = today_str
        
        msg = f"天道酬勤！已领取今日薪俸: {reward_money} 灵石。"
        if is_big_win:
            msg += "\n(恐怖如斯！竟有如此肝帝！)"
            
        logger.info(f"领取每日奖励: {reward_money} 灵石")
        return True, msg

    # ... (existing methods) ...

    def save_data(self, filepath):
        import json
        import time
        data = {
            "exp": self.exp,
            "layer_index": self.layer_index,
            "money": self.money,
            "inventory": self.inventory,
            "last_save_time": time.time(),
            "market_goods": self.market_goods,
            "last_market_refresh": self.last_market_refresh
        }
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            logger.info("数据已保存")
        except Exception as e:
            logger.error(f"保存失败: {e}")

    def load_data(self, filepath):
        import json
        import os
        if not os.path.exists(filepath):
            # 新存档，初始化坊市
            self.refresh_market()
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.exp = data.get("exp", 0)
                self.layer_index = data.get("layer_index", 0)
                self.money = data.get("money", 0)
                self.inventory = data.get("inventory", {})
                self.market_goods = data.get("market_goods", [])
                self.last_market_refresh = data.get("last_market_refresh", 0)
                
                stats = data.get("stats", {})
                self.mind = stats.get("mind", 0)
                self.body = stats.get("body", 10)
                self.affection = stats.get("affection", 0)
                
                # 结算离线
                last_time = data.get("last_save_time", 0)
                if last_time > 0:
                    self.calculate_offline_progress(last_time)
            
            # 检查刷新
            self.check_daily_refresh()
            if not self.market_goods:
                self.refresh_market()
                
            logger.info("数据已加载")
        except Exception as e:
            logger.error(f"加载失败: {e}")

    @property
    def current_layer(self):
        if self.layer_index < len(self.LAYERS):
            return self.LAYERS[self.layer_index]
        return "飞升仙界"

    @property
    def max_exp(self):
        # 简单的指数级经验曲线
        if self.layer_index < len(self.EXP_TABLE):
            return self.EXP_TABLE[self.layer_index]
        return self.EXP_TABLE[-1]

    def gain_exp(self, amount):
        self.exp += amount
        
        # 达到瓶颈
        if self.exp >= self.max_exp:
            self.exp = self.max_exp
            # 不自动升级，需要手动渡劫
        
        return False # 移除 auto level up 的返回值意义，或者是 keep signature

    def can_breakthrough(self):
        return self.exp >= self.max_exp and self.layer_index < len(self.LAYERS) - 1

    def attempt_breakthrough(self, base_success_rate=None):
        """
        尝试渡劫/突破
        :param base_success_rate: 如果提供 (0.0-1.0), 则使用此固定基础概率(丹药效果)，否则根据属性计算
        Return: (success: bool, message: str)
        """
        if not self.can_breakthrough():
            # 即使是有丹药，修为不够也不能突破 (除非是特殊的挂开药)
            return False, "修为尚未圆满，强行突破必死无疑。"
            
        import random
        
        if base_success_rate is not None:
             # 丹药突破: 固定概率 + 体魄/心魔修正(稍微小一点影响)
             # 既然是丹药，我们假设它主要看药效，但属性依然有微调
             success_rate = base_success_rate + (self.body * 0.005) - (self.mind * 0.005)
             method_str = "丹药辅助"
        else:
             # 自然突破
             # 基础成功率 50%
             # 体魄加成: 每点 +1% 
             # 心魔惩罚: 每点 -0.5%
             success_rate = 0.5 + (self.body * 0.01) - (self.mind * 0.005)
             method_str = "顺其自然"
             
        success_rate = max(0.01, min(0.99, success_rate)) # 限制范围
        
        roll = random.random()
        logger.info(f"渡劫判定({method_str}): Roll {roll:.2f} < Rate {success_rate:.2f}")
        
        if roll < success_rate:
            # 成功
            self.exp = 0 
            self.layer_index += 1
            
            # 成功奖励: 属性提升，清除少量心魔
            self.body += 2
            self.mind = max(0, self.mind - 20)
            self.talent_points += 1 # 获得天赋点
            
            msg = f"雷劫洗礼，金光护体！\n晋升【{self.current_layer}】\n体魄+2，天赋点+1"
            self.events.append(msg)
            return True, msg
        else:
            # 失败惩罚
            # ... (unchanged) ...
            loss = int(self.max_exp * 0.3)
            self.exp -= loss
            self.body = max(0, self.body - 1)
            self.mind = min(100, self.mind + 10)
            
            msg = f"渡劫失败！天雷滚滚，肉身受损。\n修为-{loss}，体魄-1，心魔+10"
            self.events.append(msg)
            return False, msg

    def gain_item(self, item_id, count=1):
        if item_id in self.inventory:
            self.inventory[item_id] += count
        else:
            self.inventory[item_id] = count
            
        # item_name = self.item_manager.get_item_name(item_id)
        # self.events.append(f"获得: {item_name} x{count}")
        # 暂时屏蔽获得物品的公共日志，避免刷屏？
        pass

    def update(self, kb_apm, mouse_apm):
        """
        根据 键鼠APM 更新状态并返回获得的收益描述
        """
        gain_msg = ""
        current_state_code = 0 
        
        # Mapping Tier
        current_tier = min(self.layer_index, 8) 
        
        # 0. 心魔与天赋判定
        # 天赋加成
        talent_exp_bonus = 1.0 + (self.talents.get("exp", 0) * 0.05)
        talent_drop_bonus = self.talents.get("drop", 0) * 0.05
        
        # 心魔惩罚: >50 开始衰减 exp 获取, 100 时无法获取 EXP
        exp_efficiency = 1.0 * talent_exp_bonus
        if self.mind > 50:
            penalty = (self.mind - 50) * 0.02 # 每点 -2%
            exp_efficiency = max(0, exp_efficiency - penalty)
            if random.random() < 0.05: # 偶尔提示
                 gain_msg = "心神不宁..."
        
        # 1. 判定状态
        if kb_apm < 30 and mouse_apm < 30:
            # IDLE
            current_state_code = 0 
            base_exp = 1 
            gain_msg = f"+{base_exp} 修为"
            if talent_exp_bonus > 1.0: gain_msg += " (天赋↑)"
            
        elif kb_apm >= 30 and mouse_apm < 30:
            # WORK: 键盘历练
            current_state_code = 2 
            base_exp = 5
            
            # 好感度加成掉落率
            drop_bonus = (self.affection * 0.002) + talent_drop_bonus # max +20% from aff, +5% * talent
            
            if random.random() < (0.05 + drop_bonus):
                drop_id = self.item_manager.get_random_material(current_tier)
                if drop_id:
                    self.gain_item(drop_id)
                    name = self.item_manager.get_item_name(drop_id)
                    gain_msg = f"探险发现: {name}!"
                    self.events.append(gain_msg) # 添加到事件日志以显示通知
                
            if not gain_msg:
                gain_msg = "+5 修为 (历练中)"

        elif kb_apm < 30 and mouse_apm >= 30:
            # READ: 悟道
            current_state_code = 3 
            base_exp = 8 
            gain_msg = "+8 修为 (悟道中)"
            
            if random.random() < 0.02:
                base_exp += 20
                gain_msg = "顿悟! +28 修为"
                # 顿悟减少心魔
                self.mind = max(0, self.mind - 5)
                
        else:
            # COMBAT: 斗法
            current_state_code = 1 
            base_exp = 15 
            gain_msg = "火力全开! +15 修为"
            
            # 战斗增加少量心魔风险
            if random.random() < 0.01:
                self.mind = min(100, self.mind + 1)
                gain_msg = "杀气过重! 心魔+1"
        
        # 应用心魔惩罚
        final_exp = int(base_exp * exp_efficiency)
        if final_exp == 0 and base_exp > 0:
             gain_msg = "心魔缠身，修为停滞！"
             
        self.gain_exp(final_exp)
        
        # --- 随机事件系统 ---
        self.tick_counter = getattr(self, 'tick_counter', 0) + 1
        if self.tick_counter >= self.event_interval:
            self.tick_counter = 0
            event = self.event_manager.get_random_event(self)
            if event:
                if event['type'] == 'random':
                    logger.info(f"触发随机事件: {event['text']}")
                    effect_texts = self.event_manager.apply_event_effect(self, event.get('effects', {}))
                    
                    full_msg = f"【机缘】{event['text']}"
                    if effect_texts:
                         full_msg += f"\n> {' '.join(effect_texts)}"
                    self.events.append(full_msg)
                else:
                    logger.info(f"触发特殊事件(未实装UI): {event['text']}")

            
        return gain_msg, current_state_code
    
    def calculate_offline_progress(self, last_timestamp):
        import time
        current_time = time.time()
        # 即使数据没有 timestamp，也要处理
        if not last_timestamp:
            return 
            
        diff = int(current_time - last_timestamp)
        if diff > 60: # 离线超过1分钟才结算
            # 离线默认按打坐计算，但收益减半 (2.5 exp/s)
            exp_gain = int(diff * 2.5)
            self.gain_exp(exp_gain)
            self.events.append(f"闭关结束，离线 {diff // 60} 分钟，获得 {exp_gain} 修为")
            
    def get_random_dialogue(self):
        dialogues = [
            "道可道，非常道...",
            "别摸了，贫道要走火入魔了！",
            "今日宜修炼，忌摸鱼。",
            "我感觉我要突破了！",
            "这位道友，我看你骨骼精奇...",
            "还不快去写代码？",
            "只有充钱才能变得更强（误",
            "修仙本是逆天而行...",
            "灵气...这里的灵气太稀薄了。",
        ]
        return random.choice(dialogues)

    def save_data(self, filepath=None):
        # filepath argument is kept for compatibility but ignored for SQLite
        from src.database import db_manager
        import json
        import time
        
        current_time = int(time.time())
        talent_json = json.dumps(self.talents)
        
        try:
            with db_manager._get_conn() as conn:
                cursor = conn.cursor()
                
                # 1. Update Status
                cursor.execute("""
                    UPDATE player_status
                    SET layer_index = ?, current_exp = ?, money = ?,
                        stat_body = ?, stat_mind = ?, stat_luck = ?,
                        talent_points = ?, talent_json = ?,
                        last_save_time = ?
                    WHERE id = 1
                """, (
                    self.layer_index, self.exp, self.money,
                    self.body, self.mind, self.affection,
                    self.talent_points, talent_json,
                    current_time
                ))
                
                # 2. Update Inventory
                # Strategy: Clear existing inventory for this user (or simple item-by-item upsert)
                # Since inventory is simple, let's just upsert all items.
                # But to handle deleted items (count 0), we should probably delete all first?
                # Actually, our inventory dict keeps 0 count items sometimes.
                # Let's clean up: remove items with <= 0 count from DB, upsert > 0.
                
                # First, upsert non-zero items
                for item_id, count in self.inventory.items():
                    if count > 0:
                        cursor.execute("""
                            INSERT INTO player_inventory (item_id, count)
                            VALUES (?, ?)
                            ON CONFLICT(item_id) DO UPDATE SET count = excluded.count
                        """, (item_id, count))
                    else:
                        cursor.execute("DELETE FROM player_inventory WHERE item_id = ?", (item_id,))
                        
                conn.commit()
                logger.info("数据已保存至数据库")
        except Exception as e:
            logger.error(f"保存失败: {e}")

    def load_data(self, filepath=None):
        from src.database import db_manager
        import json
        import os
        import time
        
        # 1. Try to load from DB
        loaded_from_db = False
        try:
            with db_manager._get_conn() as conn:
                conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM player_status WHERE id = 1")
                status = cursor.fetchone()
                
                if status and status['last_save_time']: 
                    # DB has data
                    self.layer_index = status['layer_index']
                    self.exp = status['current_exp']
                    self.money = status['money']
                    self.body = status['stat_body']
                    self.mind = status['stat_mind']
                    self.affection = status['stat_luck']
                    self.talent_points = status['talent_points']
                    if status['talent_json']:
                        self.talents = json.loads(status['talent_json'])
                    
                    last_time = status['last_save_time']
                    
                    # Load Inventory
                    cursor.execute("SELECT * FROM player_inventory")
                    inv_rows = cursor.fetchall()
                    self.inventory = {row['item_id']: row['count'] for row in inv_rows}
                    
                    loaded_from_db = True
                    
                    # Offline Progress
                    if last_time > 0:
                        self.calculate_offline_progress(last_time)
        except Exception as e:
            logger.error(f"从数据库加载失败: {e}")

        # 2. If DB empty, check for JSON migration
        if not loaded_from_db and filepath and os.path.exists(filepath):
            logger.info("数据库无存档，尝试迁移旧 JSON 存档...")
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.exp = data.get("exp", 0)
                    self.layer_index = data.get("layer_index", 0)
                    self.money = data.get("money", 0)
                    self.inventory = data.get("inventory", {})
                    # ... other fields ...
                    stats = data.get("stats", {})
                    self.mind = stats.get("mind", 0)
                    self.body = stats.get("body", 10)
                    self.affection = stats.get("affection", 0)
                    self.talents = data.get("talents", {"exp": 0, "drop": 0})
                    self.talent_points = data.get("talent_points", 0)
                    
                # Save immediately to DB
                self.save_data()
                # Rename old file to backup
                os.rename(filepath, filepath + ".bak")
                logger.info("迁移完成，旧存档已备份已 .bak")
                
                # Check Offline for JSON migration too if needed, but let's assume save_data sets current time.
                # If we want offline progress from JSON time:
                last_time = data.get("last_save_time", 0)
                if last_time > 0:
                     self.calculate_offline_progress(last_time)
                     
            except Exception as e:
                logger.error(f"JSON 迁移失败: {e}")
        
        # 3. Validation
        self.check_daily_refresh()

    def reset_to_beginning(self):
        """
        重置玩家数据回到初始状态 (转世重修)
        """
        from src.database import db_manager
        import time
        
        self.exp = 0
        self.layer_index = 0
        self.money = 0
        self.body = 10
        self.mind = 0
        self.affection = 0
        self.inventory = {}
        self.talents = {"exp": 0, "drop": 0}
        self.talent_points = 0
        
        try:
            with db_manager._get_conn() as conn:
                cursor = conn.cursor()
                # Reset Status
                cursor.execute("""
                    UPDATE player_status
                    SET layer_index=0, current_exp=0, money=0,
                        stat_body=10, stat_mind=0, stat_luck=0,
                        talent_points=0, talent_json='{}',
                        last_save_time=?
                    WHERE id=1
                """, (int(time.time()),))
                
                # Clear Inventory
                cursor.execute("DELETE FROM player_inventory")
                
                conn.commit()
            
            logger.info("玩家已转世重修 (数据重置)")
            self.events.append("【轮回】万法归一，重入灵途！")
        except Exception as e:
            logger.error(f"重置失败: {e}")
