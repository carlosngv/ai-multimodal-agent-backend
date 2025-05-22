# app/models/chat_message.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
