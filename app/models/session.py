from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    citizen_id: Optional[int] = Field(default=None, foreign_key="citizen.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    is_active_session: bool = Field(default=True)
    ended_at: Optional[datetime] = None