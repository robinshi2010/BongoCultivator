from typing import Optional
from sqlmodel import Field, SQLModel

class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs_minute"
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int
    keys_count: int = Field(default=0)
    mouse_count: int = Field(default=0)

class SystemMetadata(SQLModel, table=True):
    __tablename__ = "system_metadata"
    key: str = Field(primary_key=True)
    value: str

class EventHistory(SQLModel, table=True):
    __tablename__ = "event_history"
    event_id: str = Field(primary_key=True)
    triggered_at: int

class PlayerEvent(SQLModel, table=True):
    __tablename__ = "player_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int
    event_type: str
    message: str
