from sqlmodel import SQLModel
from app.db.session import engine
from app.models.chat_message import ChatMessage

def init_db():
    SQLModel.metadata.create_all(engine)
