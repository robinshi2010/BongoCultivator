import sqlite3
import json
import random
import time
from src.logger import logger

class EventEngine:
    def __init__(self, db_path, item_manager):
        self.db_path = db_path
        self.item_manager = item_manager
        self.events = []
        self.history = set() # Set of event_ids that have triggered (for unique events)
        
        self.reload()

    def reload(self):
        """Load events form event_definitions table"""
        from src.database import db_manager
        from src.models import EventDefinition, EventHistory
        from sqlmodel import select
        
        try:
            with db_manager.get_session() as session:
                evts = session.exec(select(EventDefinition)).all()
                self.events = []
                for e in evts:
                    if e.data_json:
                        self.events.append(json.loads(e.data_json))
                
                # Load History
                hist = session.exec(select(EventHistory)).all()
                self.history = {h.event_id for h in hist}
            
            logger.info(f"EventEngine loaded {len(self.events)} events from DB (SQLModel).")
        except Exception as e:
            logger.error(f"EventEngine load error: {e}")

    def check_triggers(self, cultivator, current_state_name='idle'):
        """
        Return an event if conditions met.
        Uses weight-based random selection among valid events.
        """
        possible_events = []
        total_weight = 0
        
        # Safe attribute access
        layer = getattr(cultivator, 'layer_index', 0)
        mind = getattr(cultivator, 'mind', 0)
        money = getattr(cultivator, 'money', 0)
        
        for evt in self.events:
            # 1. Unique Check
            if evt.get("unique", False) and evt["id"] in self.history:
                continue
                
            cond = evt.get("conditions", {})
            
            # 2. Condition Checks
            min_layer = evt.get("min_layer", cond.get("min_layer", 0))
            max_layer = evt.get("max_layer", cond.get("max_layer", 99))
            min_money = evt.get("min_money", cond.get("min_money", 0))
            min_mind = evt.get("min_mind", cond.get("min_mind", 0))
            
            # State condition (optional)
            req_state = evt.get("required_state", cond.get("required_state", None))
            if req_state and req_state != current_state_name:
                continue

            if layer < min_layer: continue
            if layer > max_layer: continue
            if money < min_money: continue
            if mind < min_mind: continue
            
            # 3. Add to pool
            w = evt.get("weight", 10)
            possible_events.append((w, evt))
            total_weight += w
            
        if not possible_events:
            return None
            
        # Weighted Random Pick
        r = random.uniform(0, total_weight)
        upto = 0
        for w, evt in possible_events:
            if r <= upto + w:
                return evt
            upto += w
            
        return possible_events[0][1]

    def trigger_event(self, event, cultivator):
        """
        Execute event effects.
        Support 'effects' dict and simpler 'choices' (auto-pick for now).
        """
        logger.info(f"Triggering event: {event.get('text', 'Unknown')} ({event['id']})")
        
        results_text = []
        
        # 1. Handle Direct Effects
        if "effects" in event:
            results_text.extend(self._apply_effects(event["effects"], cultivator))
            
        # 2. Handle Choices (Auto-resolve for now: Pick Random Choice)
        # TODO: Implement UI for choices
        if "choices" in event and event["choices"]:
            choice = random.choice(event["choices"])
            results_text.append(f"[自动选择] {choice['text']}")
            
            # Resolve choice result
            res = choice.get("result", {})
            # Chance check
            success_rate = res.get("success_chance", 1.0)
            
            if random.random() < success_rate:
                eff = res.get("success_effect", {})
                results_text.append(eff.get("text", "成功!"))
                results_text.extend(self._apply_effects(eff, cultivator))
            else:
                eff = res.get("fail_effect", {})
                results_text.append(eff.get("text", "失败!"))
                results_text.extend(self._apply_effects(eff, cultivator))
                
        # 3. Record History if Unique
        if event.get("unique", False) or event.get("is_unique", False):
            self._record_history(event["id"])
            self.history.add(event["id"])

        return "\n".join(results_text)

    def _apply_effects(self, effects, cultivator):
        """
        Apply a dict of effects { 'exp': [10, 20], 'item': {'id': x, 'count': 1} }
        """
        logs = []
        for k, v in effects.items():
            if k == "text": continue
            
            # Handle Value Range [min, max] or Single Value
            val = 0
            if isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)):
                val = random.randint(int(v[0]), int(v[1]))
            elif isinstance(v, (int, float)):
                val = int(v)
                
            # Apply
            if k == "exp":
                cultivator.gain_exp(val)
                logs.append(f"修为 {'+' if val>0 else ''}{val}")
            elif k == "money":
                cultivator.money = max(0, cultivator.money + val)
                logs.append(f"灵石 {'+' if val>0 else ''}{val}")
            elif k == "mind":
                cultivator.modify_stat("mind", val)
                logs.append(f"心魔 {'+' if val>0 else ''}{val}")
            elif k == "body":
                cultivator.modify_stat("body", val)
                logs.append(f"体魄 {'+' if val>0 else ''}{val}")
            elif k == "items":
                # items: { "id": count }
                if isinstance(v, dict):
                    for iid, count in v.items():
                        cultivator.gain_item(iid, count)
                        item_name = self.item_manager.get_item_name(iid)
                        logs.append(f"获得: {item_name} x{count}")
            
            elif k == "random_material":
                 # Dynamic material drop based on player tier
                 count = val
                 if count > 0:
                     layer = getattr(cultivator, 'layer_index', 0)
                     tier = min(layer, 8) 
                     for _ in range(count):
                         mat_id = self.item_manager.get_random_material(tier)
                         if mat_id:
                             cultivator.gain_item(mat_id, 1)
                             item_name = self.item_manager.get_item_name(mat_id)
                             logs.append(f"意外收获: {item_name}")

        return logs

    def _record_history(self, event_id):
        from src.database import db_manager
        from src.models import EventHistory
        import time
        
        try:
            with db_manager.get_session() as session:
                existing = session.get(EventHistory, event_id)
                if not existing:
                    hist = EventHistory(event_id=event_id, triggered_at=int(time.time()))
                    session.add(hist)
                    session.commit()
        except Exception as e:
            logger.error(f"History save error: {e}")
