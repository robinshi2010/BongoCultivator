from src.logger import logger
from src.database import db_manager
import time
import json
import random

class ReincarnationManager:
    """
    负责处理轮回、转世、身死道消的结算逻辑
    """
    
    @staticmethod
    def calculate_inheritance(cultivator, reason="rebirth"):
        """
        计算继承数据
        :param cultivator: Cultivator 实例
        :param reason: 'death' (身死) 或 'rebirth' (主动兵解)
        :return: legacy_data (dict)
        """
        # 1. 计算总 AP (投入 + 未投入)
        spent_ap = sum(cultivator.talents.values())
        current_ap = cultivator.talent_points
        total_ap = spent_ap + current_ap
        
        # 2. 确定继承率
        if reason == "rebirth":
            # 主动重修: 80% ~ 100% (基于境界)
            # 境界越高保留越多, layer 0-8
            layer = cultivator.layer_index
            rate = 0.8 + (layer * 0.025) # Max 0.8 + 0.2 = 1.0 at layer 8
            rate = min(1.0, rate)
        else:
            # 身死道消: 30% ~ 50%
            # 基础 30%, 体魄影响少量
            rate = 0.3 + (cultivator.body * 0.001)
            rate = min(0.5, rate)
            
        inherited_ap = int(total_ap * rate)
        
        # 3. 灵石/物品继承 (少量折算)
        # 简单策略：只继承当前灵石的 10%
        inherited_money = int(cultivator.money * 0.1)
        
        return {
            "legacy_points": inherited_ap,
            "starting_money": inherited_money,
            "rate_used": rate
        }

    @staticmethod
    def perform_reincarnation(cultivator, reason="rebirth"):
        """
        执行转世流程 (修改数据库，重置状态)
        """
        # 1. 结算
        legacy = ReincarnationManager.calculate_inheritance(cultivator, reason)
        
        new_death_count = cultivator.death_count + 1
        new_legacy_points = legacy['legacy_points']
        new_money = legacy['starting_money']
        
        # Plan 45: 计算新生气运 (0-99)
        new_luck = random.randint(0, 99)
        
        # 2. 刷新内存中的 Cultivator
        try:
            cultivator.exp = 0
            cultivator.layer_index = 0
            cultivator.money = new_money
            cultivator.body = 10
            cultivator.mind = 0
            # Plan 45: 轮回后随机给予初始气运 (0-99)
            cultivator.affection = new_luck
            cultivator.inventory = {}
            cultivator.talents = {"exp": 0, "drop": 0}
            cultivator.talent_points = new_legacy_points
            cultivator.death_count = new_death_count
            cultivator.legacy_points = new_legacy_points
            # Plan 45: 清空"一面之缘"使用记录
            cultivator.used_once_items = set()
            
            # 3. 保存到数据库 (使用 Cultivator 自身的保存逻辑确保一致性)
            cultivator.save_data()
                
            logger.info(f"轮回成功 ({reason}): 继承AP={new_legacy_points}, 继承灵石={new_money}, 新气运={new_luck}")
            
            # Log event
            msg = f"【轮回】第{new_death_count}世终了，{reason=='rebirth' and '兵解重修' or '身死道消'}。\n保留天赋点: {new_legacy_points} (继承率 {int(legacy['rate_used']*100)}%)\n本世气运: {cultivator.affection}"
            cultivator.events.append(msg)
            
            return True, legacy
            
        except Exception as e:
            logger.error(f"轮回失败: {e}")
            return False, str(e)
