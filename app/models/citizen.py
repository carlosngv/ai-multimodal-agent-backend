from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Citizen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)