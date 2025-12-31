import random
from src.logger import logger
from src.item_manager import ItemManager
from src.services.event_engine import EventEngine
from src.services.achievement_manager import achievement_manager
from src.database import DB_FILE 
from src.config import LAYERS, EXP_TABLE

class Cultivator:
    LAYERS = LAYERS
    EXP_TABLE = EXP_TABLE
    
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
        
        # 初始化 ItemManager 和 EventEngine
        self.item_manager = ItemManager()
        self.event_manager = EventEngine(DB_FILE, self.item_manager)
        
        # 天赋系统
        self.talent_points = 0
        self.talents = {
            "exp": 0,  # 修炼天赋: +5% 经验获取
            "drop": 0  # 寻宝天赋: +5% 掉落概率
        }
        
        # 每日任务相关
        self.daily_reward_claimed = None # 记录上次领奖日期 'YYYY-MM-DD'
        
        # 称号系统
        self.equipped_title = None

        # Plan 14: 轮回系统
        self.death_count = 0
        self.legacy_points = 0
        
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
        


        # 动态Tier匹配 (Plan 26)
        # 允许范围: [Current Tier - 1, Current Tier + 1]
        player_tier = min(self.layer_index, 8)
        min_tier = max(0, player_tier - 1)
        max_tier = min(8, player_tier + 1)
        
        for _ in range(6):
            # 随机决定类型
            roll = random.random()
            
            # 随机决定此商品的 Tier
            # 权重: 同阶 60%, 低阶 30%, 高阶 10%
            tier_roll = random.random()
            target_tier = player_tier
            if tier_roll < 0.3:
                 target_tier = min_tier
            elif tier_roll > 0.9:
                 target_tier = max_tier
                 
            item_id = None
            if roll < 0.6: # 60% 材料
                item_id = self.item_manager.get_random_material(target_tier)
            else: # 40% 丹药
                candidates = self.item_manager.tier_lists.get(target_tier, {}).get("pills", [])
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
        
        # 立即保存进数据库，防止刷新后只在内存
        self.save_data()
        logger.info(f"坊市商品已刷新 (Tier {min_tier}-{max_tier})")

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

    def equip_title(self, title_id):
        """装备称号"""
        # Verify ownership handled by UI calling checks, but safe to check DB here?
        # For simplicity, we assume UI only sends valid owned titles or we don't check ownership strictly here (UI does).
        # But rigorous way: check DB status=2
        self.equipped_title = title_id
        logger.info(f"Equipped Title: {title_id}")

    def unequip_title(self):
        self.equipped_title = None

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
            self.body -= 1
            if self.body <= 0:
                self.body = 0
                return False, "DEATH"

            loss = int(self.max_exp * 0.3)
            self.exp -= loss
            # self.body already decremented above
            self.mind = min(100, self.mind + 10)
            
            msg = f"渡劫失败！天雷滚滚，肉身受损。\n修为-{loss}，体魄-1，心魔+10"
            self.events.append(msg)
            return False, msg

    def gain_item(self, item_id, count=1):
        # Safeguard: Check item tier balance (Plan 17)
        item_info = self.item_manager.get_item(item_id)
        if item_info:
            item_tier = item_info.get("tier", 0)
            # Allow items up to Current Layer + 1
            max_allowed_tier = self.layer_index + 1
            
            if item_tier > max_allowed_tier:
                logger.warning(f"Economy Safeguard: Blocked Tier {item_tier} item ({item_id}) for Layer {self.layer_index} player.")
                # Fallback: Get a random material of appropriate tier
                fallback_tier = max_allowed_tier
                new_item_id = self.item_manager.get_random_material(fallback_tier)
                if new_item_id:
                    item_id = new_item_id
                    # Update info for logging if needed but main logic uses ID
                else:
                    return # Should not happen, but safe exit

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
        
        # 称号加成
        if self.equipped_title:
            eff = achievement_manager.get_title_effect(self.equipped_title)
            if eff:
                buffs = eff.get('buff', {})
                talent_exp_bonus += buffs.get('exp_mult', 0.0)
                talent_drop_bonus += buffs.get('drop_mult', 0.0)
                
                # Handling conditional buffs (e.g. Night Walker)
                if 'cond_hour_start' in buffs:
                    import datetime
                    now_hour = datetime.datetime.now().hour
                    start = buffs['cond_hour_start']
                    end = buffs['cond_hour_end']
                    # Handle cross-midnight (e.g. 22 to 4)
                    in_time = False
                    if start > end: 
                        if now_hour >= start or now_hour < end: in_time = True
                    else:
                        if start <= now_hour < end: in_time = True
                        
                    if in_time:
                         talent_drop_bonus += buffs.get('drop_mult', 0.0) # Apply bonus only if in time? 
                         # Wait, logic above adds 'drop_mult' unconditionally if I don't check key.
                         # Refine: if 'cond_hour_start' exists, the base 'drop_mult' should probably only apply then?
                         # Or usually base mult is separate.
                         # Let's assume conditional buffs are EXTRA or modifying existing.
                         # For simplicity key: 'drop_mult' is base, 'cond_...' implies conditional logic?
                         # No, let's keep it simple. If conditional keys exist, check them before applying the mult.
                         pass 
        
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
            
            # 好感度加成掉落率 (Plan 6: 降低 1/10)
            # Base 0.5% per second (~once per 3 mins)
            drop_bonus = (self.affection * 0.0002) + (talent_drop_bonus * 0.1) 
            
            if random.random() < (0.005 + drop_bonus):
                # Dynamic Drop Pool (Plan 6)
                # 80% Current, 15% Low, 5% High
                roll = random.random()
                drop_tier = current_tier
                if roll < 0.15 and current_tier > 0:
                    drop_tier = current_tier - 1
                elif roll > 0.95 and current_tier < 8:
                    drop_tier = current_tier + 1
                    
                drop_id = self.item_manager.get_random_material(drop_tier)
                if drop_id:
                    self.gain_item(drop_id)
                    name = self.item_manager.get_item_name(drop_id)
                    gain_msg = f"探险发现: {name}!"
                    self.events.append(gain_msg)
                
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
        
        # --- 成就系统检查 ---
        new_unlocks = achievement_manager.check_periodic(self)
        for ach in new_unlocks:
            msg = f"【天道感应】达成成就 [{ach['name']}]！"
            reward_desc = ""
            if ach['reward_type'] == 'item':
                 # Value format: "id:count"
                 parts = ach['reward_value'].split(':')
                 item_id = parts[0]
                 count = parts[1] if len(parts) > 1 else 1
                 item_name = self.item_manager.get_item_name(item_id)
                 reward_desc = f"(奖励物品: {item_name} x{count})"
            elif ach['reward_type'] == 'title':
                 reward_desc = "(奖励称号)"
            self.events.append(f"{msg}\n{reward_desc}")

        # --- 随机事件系统 ---
        self.tick_counter = getattr(self, 'tick_counter', 0) + 1
        if self.tick_counter >= self.event_interval:
            self.tick_counter = 0
            
            # Map code to state string
            state_map = {0: "IDLE", 1: "COMBAT", 2: "WORK", 3: "READ"}
            state_name = state_map.get(current_state_code, "IDLE")
            
            event = self.event_manager.check_triggers(self, state_name)
            if event:
                result_msg = self.event_manager.trigger_event(event, self)
                event_msg = f"【机缘】{event['title']}\n{event['text']}"
                if result_msg:
                     event_msg += f"\n> {result_msg}"
                self.events.append(event_msg)
                
                # Make sure to show it in UI
                if gain_msg:
                    gain_msg += "\n\n" + event_msg
                else:
                    gain_msg = event_msg

            
        return gain_msg, current_state_code
    
    def calculate_offline_progress(self, last_timestamp):
        import time
        current_time = time.time()
        # 即使数据没有 timestamp，也要处理
        if not last_timestamp:
            return 
            
        diff = int(current_time - last_timestamp)
        if diff > 60: # 离线超过1分钟才结算
            # 离线默认按打坐计算，但收益减半 (1.0 exp/s, Plan 4 benchmark)
            exp_gain = int(diff * 1.0)
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
        # filepath is ignored
        from src.database import db_manager
        from src.models import PlayerStatus, PlayerInventory, MarketStock
        from sqlmodel import delete
        import json
        import time
        
        current_time = int(time.time())
        talent_json_str = json.dumps(self.talents)
        
        try:
            with db_manager.get_session() as session:
                # 1. Update PlayerStatus
                player = session.get(PlayerStatus, 1)
                if not player:
                    player = PlayerStatus(id=1)
                    session.add(player)
                
                player.layer_index = self.layer_index
                player.current_exp = self.exp
                player.money = self.money
                player.stat_body = self.body
                player.stat_mind = self.mind
                player.stat_luck = self.affection
                player.talent_points = self.talent_points
                player.talent_json = talent_json_str
                player.last_save_time = current_time
                player.equipped_title = self.equipped_title
                player.death_count = self.death_count
                player.legacy_points = self.legacy_points
                player.daily_reward_claimed = self.daily_reward_claimed
                player.last_market_refresh_time = int(self.last_market_refresh)
                
                session.add(player)
                
                # 2. Update Inventory
                # Clear and re-insert
                session.exec(delete(PlayerInventory))
                
                for iid, count in self.inventory.items():
                    if count > 0:
                        inv_item = PlayerInventory(item_id=iid, count=count)
                        session.add(inv_item)
                        
                # 3. Update Market Stock
                session.exec(delete(MarketStock))
                for goods in self.market_goods:
                    stock = MarketStock(
                        item_id=goods['id'],
                        price=goods['price'],
                        discount=goods['discount']
                    )
                    session.add(stock)
                
                session.commit()
                # logger.debug("数据已保存 (SQLModel)")
                
        except Exception as e:
            logger.error(f"保存失败: {e}")

    def load_data(self, filepath=None):
        from src.database import db_manager
        from src.models import PlayerStatus, PlayerInventory, MarketStock
        from sqlmodel import select
        import json
        
        try:
            with db_manager.get_session() as session:
                # 1. Load Status
                player = session.get(PlayerStatus, 1)
                
                if player and player.last_save_time:
                    self.layer_index = player.layer_index
                    self.exp = player.current_exp
                    self.money = player.money
                    self.body = player.stat_body
                    self.mind = player.stat_mind
                    self.affection = player.stat_luck
                    self.talent_points = player.talent_points
                    if player.talent_json:
                        self.talents = json.loads(player.talent_json)
                        
                    self.equipped_title = player.equipped_title
                    self.death_count = player.death_count
                    self.legacy_points = player.legacy_points
                    self.daily_reward_claimed = player.daily_reward_claimed
                    self.last_market_refresh = player.last_market_refresh_time
                    
                    # 2. Load Inventory
                    inv_items = session.exec(select(PlayerInventory)).all()
                    self.inventory = {item.item_id: item.count for item in inv_items}
                    
                    # 3. Load Market
                    market_items = session.exec(select(MarketStock)).all()
                    self.market_goods = []
                    for m in market_items:
                        self.market_goods.append({
                            "id": m.item_id,
                            "price": m.price,
                            "discount": m.discount
                        })
                        
                    # Offline Progress
                    if player.last_save_time > 0:
                        self.calculate_offline_progress(player.last_save_time)
                else:
                    logger.info("新存档 (或数据为空)，初始化...")
                    self.refresh_market()
                    
        except Exception as e:
            logger.error(f"加载失败: {e}")
            
        self.check_daily_refresh()


    def reset_to_beginning(self):
        """
        重置玩家数据回到初始状态 (转世重修)
        """
        from src.services.reincarnation_manager import ReincarnationManager
        success, res = ReincarnationManager.perform_reincarnation(self, reason="rebirth")
        if not success:
             logger.error(f"重置失败: {res}")
    def process_secret_command(self, code):
        """
        处理作弊/秘籍指令
        :param code: 输入的指令字符串
        :return: (success: bool, message: str)
        """
        code = code.strip()
        
        # 1. isosyourdaddy -> 炼气(0) 到 筑基(1)
        if code.lower() == "whosyourdaddy":
            if self.layer_index == 0:
                self.layer_index = 1
                self.exp = 0
                self.body += 5
                self.mind = 0
                self.talent_points += 1
                msg = "【天道作弊】神力加持！你已直接晋升筑基期！"
                self.events.append(msg)
                return True, msg
            else:
                return False, "当前境界无法使用此密令 (仅炼气期可用)"
                
        # 2. 上上下下左左右右baba -> 筑基(1) 到 金丹(2)
        elif code == "上上下下左左右右baba":
            if self.layer_index == 1:
                self.layer_index = 2
                self.exp = 0
                self.body += 10
                self.mind = 0
                self.talent_points += 1
                msg = "【天道作弊】魂斗罗附体！你已直接晋升金丹大道！"
                self.events.append(msg)
                return True, msg
            else:
                return False, "当前境界无法使用此密令 (仅筑基期可用)"
                
        # 3. haiwangshabi -> 金丹(2) 到 元婴(3)
        elif code == "haiwangshabi":
            if self.layer_index == 2:
                self.layer_index = 3
                self.exp = 0
                self.body += 20
                self.mind = 0
                self.talent_points += 1
                msg = "【天道作弊】海王之力附体？你已直接晋升元婴老祖！"
                self.events.append(msg)
                return True, msg
            else:
                return False, "当前境界无法使用此密令 (仅金丹期可用)"
                
        # 4. reborn -> 重置 (Existing logic wrapper)
        elif code.lower() == "laozibuganle":
             self.reset_to_beginning()
             return True, "已转世重修。"

        # 5. Unconditional Level Up (Debug)
        elif code == "haiwangdashabi":
             if self.layer_index < 8:
                 self.layer_index += 1
                 self.exp = 0
                 self.body += 10
                 self.mind = 0
                 self.talent_points += 1
                 current_layer_name = self.LAYERS[self.layer_index]
                 msg = f"【天道作弊】海王大傻逼显灵！强行晋升至【{current_layer_name}】！"
                 self.events.append(msg)
                 return True, msg
             else:
                 return False, "已达巅峰，无法再升！"
             
        return False, "天机不可泄露 (无效密令)"
