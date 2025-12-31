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

    # ... (check_triggers and trigger_event remain same logic, just pure python) ...

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
