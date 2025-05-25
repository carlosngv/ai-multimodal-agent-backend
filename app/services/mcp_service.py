import json
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

from typing import Optional

from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from pathlib import Path
from textwrap import dedent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

from pydantic import BaseModel

class Attraction(BaseModel):
    name: str
    description: str
    location: str
    rating: Optional[float] = None
    visit_duration: Optional[str] = None
    best_time_to_visit: Optional[str] = None

class SystemFileResponse(BaseModel):
    file: str
    description: str
    directory: str
    location: str

# ? Doc: https://docs.agno.com/tools/mcp/mcp#model-context-protocol-mcp
class MCPService:
    settings = Settings()
    agent = None
    
    
    async def run_agent(self):
        
        # Initialize the MCP server
        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(Path(__file__).parent.parent.parent.parent),
            ],
        )

        try:
            async with MCPTools(server_params=server_params) as mcp_tools:
                openrouter_api_key = os.getenv("OPENROUTER_KEY")
                self.agent = Agent(
                    model=OpenRouter(
                        id="meta-llama/llama-3.3-8b-instruct:free", 
                        api_key=os.getenv("OPENROUTER_KEY")

                    ),
                    
                    tools=[mcp_tools],
                    instructions=("""\
                        You are a filesystem assistant. Help users explore files and directories.

                        - Navigate the filesystem to answer questions
                        - Use the list_allowed_directories tool to find directories that you can access
                        - Provide clear context about files you examine
                        - Use headings to organize your responses
                        - Be concise and focus on relevant information\
                    """),
                    markdown=True,
                    # response_model=SystemFileResponse,
                )                
        except ValueError as e:
            print('ERROR:', e)
            
    async def run_googlemaps_agent(self):
                # Initialize the MCP server
        
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={
                "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")
            }
        )

        try:
            async with MCPTools(server_params=server_params) as mcp_tools:

                self.agent = Agent(
                    model=OpenRouter(
                        id="meta-llama/llama-3.3-8b-instruct:free", 
                        
                        api_key=os.getenv("OPENROUTER_KEY")
                    ),
                    
                    tools=[mcp_tools],
                    instructions=dedent("""\
                        You are an agent that helps find attractions, points of interest,
                        and provides directions in travel destinations. Help plan travel
                        routes and find interesting places to visit for a given location and date.\
                    """),
                    markdown=True,
                    response_model=Attraction,
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
    
    async def chat(self, message: str, citizen_email: str ):
        message = message.replace('MCP:', '')
        await self.run_agent()
        for db in get_session():
            citizen = self.get_or_create_citizen(db, citizen_email)
            chat_session = self.create_session_for_citizen(db, citizen.id)
            session_id = chat_session.id
            break        

        # run_response = self.run_agent(message)
        run_response = await self.agent.arun(message)
        for session in get_session():
            msg = ChatMessage(
                session_id=session_id,
                message=message,
                # response=json.dumps(run_response.content.dict(), ensure_ascii=False)
                response=run_response.content
            )
            session.add(msg)
            session.commit()
        return run_response.content
            
    async def locate_attractions(self, message: str, citizen_email: str ):
        message = message.replace('MCP:', '')
        await self.run_googlemaps_agent()
        for db in get_session():
            citizen = self.get_or_create_citizen(db, citizen_email)
            chat_session = self.create_session_for_citizen(db, citizen.id)
            session_id = chat_session.id
            break        

        # run_response = self.run_agent(message)
        run_response = await self.agent.arun(message, stream=True)
        
        try:
            for session in get_session():
                msg = ChatMessage(
                    session_id=session_id,
                    message=message,
                    response=json.dumps(run_response.content.dict(), ensure_ascii=False)
                )
                session.add(msg)
                session.commit()
        except ValueError as e:
            return "Problemas al consultar atracción"
        
        
        return run_response.content


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
