import os
from app.config.settings import Settings
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.embedder.google import GeminiEmbedder
from agno.agent import Agent


from app.config.settings import Settings
from app.models.session import Session
from app.db.session import get_session
from app.models.chat_message import ChatMessage
from app.models.citizen import Citizen
from sqlmodel import select

from agno.models.openrouter import OpenRouter



class KnowledgeService:
    settings = Settings()
    DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}"

    def __init__(self):
        try:
            
            pdf_knowledge_base = PDFUrlKnowledgeBase(
                urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
                vector_db=PgVector(
                    table_name="recipes",
                    db_url=self.DATABASE_URL,
                    search_type=SearchType.hybrid
                ),
            )
            self.agent = Agent(
                model=OpenRouter(
                    id="qwen/qwen2.5-vl-32b-instruct:free", 
                    api_key=self.settings.openrouter_key,
                ),
                knowledge=pdf_knowledge_base,
                add_references=True,
                search_knowledge=False,
                markdown=True,
            )
            self.agent.knowledge.load(recreate=False)
        except ValueError as e:
            print('ERROR:', e)

    async def search(self, query: str, citizen_email: str):
        for db in get_session():
            citizen = self.get_or_create_citizen(db, citizen_email)
            chat_session = self.create_session_for_citizen(db, citizen.id)
            session_id = chat_session.id
            break
        run_response = await self.agent.arun(query, stream=True)
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
                message=query,
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