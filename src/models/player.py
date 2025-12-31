from typing import Optional
from sqlmodel import Field, SQLModel

class PlayerStatus(SQLModel, table=True):
    __tablename__ = "player_status"
    
    id: int = Field(default=1, primary_key=True)
    layer_index: int = Field(default=0)
    current_exp: int = Field(default=0)
    money: int = Field(default=0)
    
    stat_body: int = Field(default=10)
    stat_mind: int = Field(default=0)
    stat_luck: int = Field(default=0)
    
    talent_points: int = Field(default=0)
    talent_json: str = Field(default="{}") # Store as JSON string
    
    last_save_time: int = Field(default=0)
    last_login_time: int = Field(default=0)
    
    equipped_title: Optional[str] = Field(default=None)
    death_count: int = Field(default=0)
    legacy_points: int = Field(default=0)
    daily_reward_claimed: Optional[str] = Field(default=None)
    last_market_refresh_time: int = Field(default=0)

class PlayerInventory(SQLModel, table=True):
    __tablename__ = "player_inventory"
    item_id: str = Field(primary_key=True)
    count: int = Field(default=0)

class MarketStock(SQLModel, table=True):
    __tablename__ = "market_stock"
    slot_id: Optional[int] = Field(default=None, primary_key=True)
    item_id: str
    count: int = Field(default=1)
    price: int
    discount: float
