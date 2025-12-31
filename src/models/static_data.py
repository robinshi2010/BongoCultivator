from typing import Optional
from sqlmodel import Field, SQLModel

class ItemDefinition(SQLModel, table=True):
    __tablename__ = "item_definitions"
    id: str = Field(primary_key=True)
    name: str
    type: str
    tier: int
    description: Optional[str] = None
    price: int
    effect_json: Optional[str] = None

class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"
    result_item_id: str = Field(primary_key=True)
    ingredients_json: str
    craft_time: int
    success_rate: float

class Achievement(SQLModel, table=True):
    __tablename__ = "achievements"
    id: str = Field(primary_key=True)
    category: str
    name: str
    desc: str
    condition_type: str
    condition_target: str
    threshold: int
    reward_type: str
    reward_value: str
    is_hidden: int = Field(default=0)
    status: int = Field(default=0)
    unlocked_at: Optional[int] = None

class EventDefinition(SQLModel, table=True):
    __tablename__ = "event_definitions"
    id: str = Field(primary_key=True)
    type: str
    weight: int
    data_json: str
