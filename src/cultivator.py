import random
from src.logger import logger

class Cultivator:
    LAYERS = [
        "炼气期", "筑基期", "金丹期", "元婴期", "化神期", "炼虚期", "合体期", "大乘期", "渡劫期"
    ]
    
    ITEMS = {
        "聚气丹": {"desc": "增加50点修为", "type": "exp", "value": 50, "price": 10},
        "筑基丹": {"desc": "突破筑基期的必备丹药", "type": "breakthrough", "price": 100},
        "洗髓草": {"desc": "洗练筋骨，略微增加体魄", "type": "material", "price": 5},
        "天雷竹": {"desc": "稀有炼器材料", "type": "material", "price": 50},
    }

    def __init__(self):
        self.exp = 0
        self.layer_index = 0
        self.money = 0 # 灵石
        self.inventory = {} # 物品栏 {name: count}
        self.events = [] # 事件日志

    @property
    def current_layer(self):
        if self.layer_index < len(self.LAYERS):
            return self.LAYERS[self.layer_index]
        return "飞升仙界"

    @property
    def max_exp(self):
        # 简单的指数级经验曲线
        return 100 * (2 ** self.layer_index)

    def gain_exp(self, amount):
        old_layer = self.layer_index
        self.exp += amount
        leveled_up = False
        
        # 自动突破检查 (简单模式：满了就升级，未来可以加入渡劫卡点)
        if self.exp >= self.max_exp:
            # 这里简单处理，直接升级并保留溢出经验
            self.exp -= self.max_exp
            self.layer_index += 1
            leveled_up = True
            
            # 突破奖励
            self.events.append(f"突破成功！晋升为【{self.current_layer}】")
            
        return leveled_up

    def gain_item(self, item_name, count=1):
        if item_name in self.inventory:
            self.inventory[item_name] += count
        else:
            self.inventory[item_name] = count
        self.events.append(f"获得: {item_name} x{count}")

    def update(self, apm):
        """
        根据 APM 更新状态并返回获得的收益描述
        """
        gain_msg = ""
        is_combat = apm > 60
        
        # 1. 基础收益
        if is_combat:
            # 战斗/历练：高几率获得灵石，低几率掉落物品
            base_exp = 2
            self.money += 1
            gain_msg = "+2 修为, +1 灵石"
            
            # 随机掉落
            if random.random() < 0.05: # 5% 掉落
                drop_item = random.choice(["洗髓草", "聚气丹", "天雷竹"])
                self.gain_item(drop_item)
                gain_msg += f", 掉落 [{drop_item}]!"
                
        else:
            # 打坐：纯经验
            base_exp = 5
            gain_msg = "+5 修为"
            
            # 随机顿悟
            if random.random() < 0.02: # 2% 顿悟
                bonus = 20
                base_exp += bonus
                gain_msg += f", 顿悟! (+{bonus}修为)"
        
        self.gain_exp(base_exp)
            
        return gain_msg, is_combat
    
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

    def save_data(self, filepath):
        import json
        import time
        data = {
            "exp": self.exp,
            "layer_index": self.layer_index,
            "money": self.money,
            "inventory": self.inventory,
            "last_save_time": time.time()
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
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.exp = data.get("exp", 0)
                self.layer_index = data.get("layer_index", 0)
                self.money = data.get("money", 0)
                self.inventory = data.get("inventory", {})
                
                # 结算离线
                last_time = data.get("last_save_time", 0)
                if last_time > 0:
                    self.calculate_offline_progress(last_time)
                    
            logger.info("数据已加载")
        except Exception as e:
            logger.error(f"加载失败: {e}")
