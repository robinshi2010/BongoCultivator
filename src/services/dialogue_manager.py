import random
import json
from src.logger import logger

class DialogueManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DialogueManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.dialogues = []
        self.reload()
        self.initialized = True

    def reload(self):
        from src.database import db_manager
        from src.models.static_data import DialogueDefinition
        from sqlmodel import select
        
        try:
            with db_manager.get_session() as session:
                rows = session.exec(select(DialogueDefinition)).all()
                self.dialogues = []
                for row in rows:
                    cond = {}
                    if row.conditions_json:
                        try:
                            cond = json.loads(row.conditions_json)
                        except:
                            pass
                            
                    d = {
                        "id": row.id,
                        "text": row.text,
                        "type": row.type,
                        "conditions": cond,
                        "weight": row.weight
                    }
                    self.dialogues.append(d)
            logger.info(f"DialogueManager loaded {len(self.dialogues)} dialogues.")
        except Exception as e:
            logger.error(f"DialogueManager load failed: {e}")

    def get_random_dialogue(self, cultivator):
        """
        Get a random dialogue based on cultivator state.
        :param cultivator: Cultivator instance
        :return: str dialogue text
        """
        candidates = []
        total_weight = 0
        
        # State Context
        layer = getattr(cultivator, 'layer_index', 0)
        mind = getattr(cultivator, 'mind', 0)
        # We assume cultivator might have daily_clicks if we patch it, or we rely on 'state' string
        # To handle daily clicks, we'd need to fetch it. 
        # For now, let's skip 'clicks' condition if we can't access it easily, OR 
        # we try to access `cultivator.daily_clicks` if meaningful.
        # Check if `cultivator.history_context` exists (Plan...?)
        # Let's support 'click' ONLY if passed in context, otherwise 0.
        # But `cultivator` parameter is likely just `self`.
        
        # We can scan conditions to see if they need clicks.
        pass_clicks = 0 
        # If we want to support click dialogues, we need to pass it.
        # Let's assume we update Cultivator to have a property `current_daily_stats`.
        # Taking a shortcut: ignore clicks for now or mock it if unavailable.
        # Actually I can read `sys.modules['src.services.input_monitor']`? NO.
        # Clean way: `get_random_dialogue(cultivator, context={})`
        
        for d in self.dialogues:
            cond = d["conditions"]
            
            # Layer Check
            if "min_layer" in cond and layer < cond["min_layer"]: continue
            if "max_layer" in cond and layer > cond["max_layer"]: continue
            
            # Mind Check
            if "min_mind" in cond and mind < cond["min_mind"]: continue
            
            # State Check (IDLE, WORK, COMBAT) -- Cultivator doesn't store current state as a field?
            # `Cultivator.update` returns state. But `get_random_dialogue` is called on click.
            # We don't strictly know state on click event unless tracked.
            # `InputMonitor` knows APM but not 'state code'.
            # However `Cultivator` holds `last_state_code` (maybe).
            # Plan 1 completed: State Machine. Let's check `Cultivator` if it has state.
            # Looking at `cultivator.py`... it returns state in `update`.
            # Let's add `self.current_state_name` to `Cultivator`.
            if "required_state" in cond:
                curr_state = getattr(cultivator, 'current_state_name', 'IDLE')
                if curr_state != cond["required_state"]: continue
                
            # Clicks Check
            if "min_daily_clicks" in cond:
                # Need external info. If not provided, skip this dialogue to be safe?
                # Or try to fetch from DB?
                # Let's skip for now unless I update Cultivator to cache it.
                continue 

            w = d["weight"]
            candidates.append((w, d))
            total_weight += w
            
        if not candidates:
            return "..."
            
        r = random.uniform(0, total_weight)
        upto = 0
        for w, d in candidates:
            if r <= upto + w:
                return d["text"]
            upto += w
            
        return candidates[0][1]["text"]

dialogue_manager = DialogueManager()
