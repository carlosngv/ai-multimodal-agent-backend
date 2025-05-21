# app/models/chat_message.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
