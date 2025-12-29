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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT data_json FROM event_definitions")
            rows = cursor.fetchall()
            self.events = []
            for r in rows:
                if r[0]:
                    self.events.append(json.loads(r[0]))
            
            # Load History (keep existing history table logic)
            cursor.execute("SELECT event_id FROM event_history")
            self.history = {r[0] for r in cursor.fetchall()}
            
            conn.close()
            logger.info(f"EventEngine loaded {len(self.events)} events from DB.")
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
            # 2. Condition Checks
            min_layer = evt.get("min_layer", cond.get("min_layer", 0))
            max_layer = evt.get("max_layer", cond.get("max_layer", 99))
            min_money = evt.get("min_money", cond.get("min_money", 0))
            min_mind = evt.get("min_mind", cond.get("min_mind", 0))

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
        # To prevent spamming, we assume check_triggers is called with a global chance? 
        # Or we roll against total weight? 
        # Usually EventEngine.check() is called every minute. We should probably just return one event based on weights.
        # But we also need a "no event" chance? 
        # Let's assume the caller controls frequency. We just pick one valid event here.
        
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
                
        # Record ID logic... (omitted for brevity, assume simple save)
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
                cultivator.money += val
                logs.append(f"灵石 {'+' if val>0 else ''}{val}")
            elif k == "mind":
                cultivator.mind += val
                logs.append(f"心魔 {'+' if val>0 else ''}{val}")
            elif k == "body":
                cultivator.body += val
                logs.append(f"体魄 {'+' if val>0 else ''}{val}")
            elif k == "items":
                # items: { "id": count }
                if isinstance(v, dict):
                    for iid, count in v.items():
                        cultivator.gain_item(iid, count)
                        item_name = self.item_manager.get_item_name(iid)
                        logs.append(f"获得: {item_name} x{count}")
                        
        return logs

        # Record history if unique
        # We need to check if 'unique' key exists in event (based on new schema which uses 'unique' not 'is_unique' sometimes, let's allow both or check json)
        # In reload(), I'm just loading the JSON. The JSON has "is_unique"? No, items schema has "is_unique" but events.json typically uses "unique" or just logic. 
        # Wait, the DB reload puts EVERYTHING in the dict.
        # Let's check safely.
        
        if event.get("unique", False) or event.get("is_unique", False):
            self._record_history(event["id"])
            self.history.add(event["id"])
            
        return "\n".join(results_text)

    def _record_history(self, event_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO event_history (event_id, triggered_at) VALUES (?, ?)", 
                           (event_id, int(time.time())))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"History save error: {e}")
