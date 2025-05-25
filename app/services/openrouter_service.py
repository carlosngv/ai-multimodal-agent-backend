import os
import base64
import mimetypes
import fitz

from typing import AsyncGenerator
from app.config.settings import Settings
from app.models.session import Session
from app.db.session import get_session
from app.models.chat_message import ChatMessage
from app.models.citizen import Citizen
from sqlmodel import select

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.storage.postgres import PostgresStorage


class OpenRouterService:
    settings = Settings()
    DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}"
    
    def create_agent(self, session_id):
        try:
            
            return Agent(
                model=OpenRouter(
                    id="qwen/qwen2.5-vl-32b-instruct:free", 
                    api_key=os.getenv("OPENROUTER_KEY")
                ),
                storage=PostgresStorage(table_name="agent_sessions", db_url=self.DATABASE_URL, schema='public'),
                session_id=session_id,
                add_history_to_messages=True,
            )
        except ValueError as e:
            print('ERROR:', e)

    def get_text_from_pdf(self, base64_data: str) -> str:
        try:
            binary = base64.b64decode(base64_data)
            pdf = fitz.open(stream=binary, filetype="pdf")
            return "\n".join(page.get_text() for page in pdf)
        except Exception as e:
            return f"[Error al procesar PDF: {str(e)}]"

    def build_pdf_message(self, file):
        return {
            "type": "file",
            "file": {
                "filename": file["file_name"],
                "file_data": f"data:application/pdf;base64,{file["data"]}"
            }
        }
    def build_image_message(self, file):
        mime_type, _ = mimetypes.guess_type(file["file_name"])
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{file['data']}"
            }
        }
    
    async def chat(self, message: str, citizen_email: str, file: dict | None = None, ) -> AsyncGenerator[str, None]:
        
        session_id = 0
        for db in get_session():
            citizen = self.get_or_create_citizen(db, citizen_email)
            chat_session = self.create_session_for_citizen(db, citizen.id)
            session_id = chat_session.id
            break
        agent = self.create_agent(session_id)
        messages = [
            {
                "role": "user", 
                "content": message
            }
        ]
        
        if file:
            if file["file_name"].lower().endswith(".pdf"):
                pdf_content = self.get_text_from_pdf(file["data"])
                messages = f"{message} Contenido del PDF: {file['file_name']}: {pdf_content}"
                # messages.append(self.build_pdf_message(file))
                
            elif file["file_name"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                messages.append(self.build_image_message(file))
                
            else:
                messages = f" [Archivo {file['file_name']} no es compatible, se ignora]"
        else:
            messages = message
        run_response = await agent.arun(messages, stream=True)
        full_response = ""
        async for chunk in run_response:
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
        if not full_response:
            full_response = "[Sin respuesta del modelo]"
        else:
            full_response = full_response[:150]
        for session in get_session():
            msg = ChatMessage(
                session_id=session_id,
                message=message,
                response=full_response
            )
            session.add(msg)
            session.commit()


    def get_or_create_citizen(self, db, email):
        citizen = db.exec(select(Citizen).where(Citizen.email == email)).first()
        if not citizen:
            citizen = Citizen(email=email)
            db.add(citizen)
            db.commit()
            db.refresh(citizen)
        return citizen

    def create_session_for_citizen(self, db, citizen_id):
        session = db.exec(select(Session).where(Session.citizen_id == citizen_id)).first()
        if not session:
            session = Session(citizen_id=citizen_id)
            db.add(session)
            db.commit()
            db.refresh(session)
        
        return session
