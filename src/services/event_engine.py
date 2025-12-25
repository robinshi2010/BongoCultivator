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
        """Load events and history from DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load Events
            cursor.execute("SELECT id, title, type, trigger_json, description, outcomes_json, is_unique FROM game_events")
            rows = cursor.fetchall()
            self.events = []
            for r in rows:
                self.events.append({
                    "id": r[0],
                    "title": r[1],
                    "type": r[2],
                    "triggers": json.loads(r[3]),
                    "text": r[4],
                    "outcomes": json.loads(r[5]),
                    "is_unique": bool(r[6])
                })
                
            # Load History
            cursor.execute("SELECT event_id FROM event_history")
            self.history = {r[0] for r in cursor.fetchall()}
            
            conn.close()
            logger.info(f"EventEngine loaded {len(self.events)} events, {len(self.history)} history records.")
        except Exception as e:
            logger.error(f"EventEngine load error: {e}")

    def check_triggers(self, cultivator, current_state_name):
        """
        Check all events and return one (or None) to trigger.
        Prioritize Unique > Rare > Common.
        """
        possible_events = []
        
        # Current Context
        # attributes might be dict or object attributes. 
        # Cultivator has: layer_index, property_manager (mind, luck, body implicit?), state
        
        # We need to access cultivator attributes safely
        layer = getattr(cultivator, 'layer_index', 0)
        # For now assume mind/luck are accessible on cultivator.property_manager or inventory
        # The prompt implies we have stats. Let's assume standard ones or query properties.
        # But looking at cultivator.py, properties like 'mind' (心魔) are in 'properties' dict presumably?
        # Actually cultivator usually manages exp, layer. 
        # Let's peek cultivator to be sure about stats access
        
        mind = getattr(cultivator, 'mind', 0)
        luck = getattr(cultivator, 'affection', 0) # affection is luck
        
        for evt in self.events:
            # 1. Check Uniqueness
            if evt["is_unique"] and evt["id"] in self.history:
                continue
                
            triggers = evt["triggers"]
            
            # 2. Check Layer
            if "min_layer" in triggers and layer < triggers["min_layer"]: continue
            if "max_layer" in triggers and layer > triggers["max_layer"]: continue
            
            # 3. Check State
            if "state" in triggers and triggers["state"] != current_state_name: continue
            
            # 4. Check Stats
            if "mind_min" in triggers and mind < triggers["mind_min"]: continue
            if "mind_max" in triggers and mind > triggers["mind_max"]: continue
            if "luck_min" in triggers and luck < triggers["luck_min"]: continue
            
            # 5. Chance Check (Optimization: Check chance last or collect all qualified then roll?)
            # If we collect all qualified, we can do weighted roll.
            # But the 'chance' in JSON implies independent probability tick.
            # Let's collect ALL qualified events, then filter by their individual probabilities.
            
            chance = triggers.get("chance", 0.01)
            # Roll for eligibility
            if random.random() < chance:
                possible_events.append(evt)
                
        if not possible_events:
            return None
            
        # Select one event
        # If multiple, pick random (or prioritize rarity)
        # Simple approach: Pick random
        return random.choice(possible_events)

    def trigger_event(self, event, cultivator):
        """
        Execute the event outcomes and log history
        """
        logger.info(f"Triggering event: {event['title']} ({event['id']})")
        
        outcomes = event["outcomes"]
        results_text = []
        
        # Apply Outcomes
        for out in outcomes:
            otype = out.get("type")
            
            if otype == "random":
                # Handle nested random outcomes
                options = out.get("options", [])
                total_w = sum(o["weight"] for o in options)
                r = random.uniform(0, total_w)
                upto = 0
                selected_outs = []
                for opt in options:
                    if r <= upto + opt["weight"]:
                        selected_outs = opt["outcomes"]
                        break
                    upto += opt["weight"]
                
                # Recursive apply (depth 1)
                for sub_out in selected_outs:
                    res = self._apply_single_outcome(sub_out, cultivator)
                    if res: results_text.append(res)
            else:
                res = self._apply_single_outcome(out, cultivator)
                if res: results_text.append(res)
                
        # Record history if unique
        if event["is_unique"]:
            self._record_history(event["id"])
            self.history.add(event["id"])
            
        return "\n".join(results_text)

    def _apply_single_outcome(self, out, cultivator):
        otype = out.get("type")
        val = out.get("val", 0)
        
        if otype == "exp":
            cultivator.gain_exp(val)
            return f"修为 {'+' if val>0 else ''}{val}"
            
        elif otype == "mind":
            old = getattr(cultivator, 'mind', 0)
            cultivator.mind = max(0, old + val)
            return f"心魔 {'+' if val>0 else ''}{val}"
            
        elif otype == "luck":
            old = getattr(cultivator, 'affection', 0)
            cultivator.affection = max(0, old + val)
            return f"气运 {'+' if val>0 else ''}{val}"
            
        elif otype == "money":
            old = getattr(cultivator, 'money', 0)
            cultivator.money = max(0, old + val)
            return f"灵石 {'+' if val>0 else ''}{val}"
            
        elif otype == "item":
            iid = out.get("id")
            count = out.get("count", 1)
            cultivator.gain_item(iid, count)
            # Get item name
            info = self.item_manager.get_item(iid)
            name = info["name"] if info else iid
            return f"获得: {name} x{count}"
            
        elif otype == "body":
            old = getattr(cultivator, 'body', 10) # Default body to 10 if not set
            cultivator.body = max(1, old + val) # Body should not go below 1
            return f"体魄 {'+' if val>0 else ''}{val}"
             
        return None

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
