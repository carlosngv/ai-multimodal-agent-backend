import base64
import mimetypes
import fitz

from typing import Any, AsyncGenerator
from app.config.settings import Settings

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat

from app.db.session import get_session
from app.models.chat_message import ChatMessage

class OpenRouterService:
    settings = Settings()
    
    def __init__(self):
        try:
            self.agent = Agent(
                model=OpenAIChat(
                    id="qwen/qwen2.5-vl-32b-instruct:free", 
                    api_key="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", 
                    base_url="https://openrouter.ai/api/v1",
                ),
            )
        except ValueError as e:
            print('ERROR:', e)
    
    async def chat_with_file(self, data):
        file = data['file']
        message = data['message']
        print({ "message": message })

        messages = [{"role": "user", "content": message}]
        if file["file_name"].lower().endswith(".pdf"):
            pdf_content = self.get_text_from_pdf(file["data"])
            messages[0]["content"] += f" Contenido del PDF {file['file_name']}: {pdf_content}"
        elif file["file_name"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            messages.append(self.build_image_message(file))
        else:
            messages[0]["content"] += f" [Archivo {file['file_name']} no es compatible, se ignora]"

        run_response = await self.agent.arun(messages, stream=True)
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
                message=message,
                response=full_response
            )
            session.add(msg)
            session.commit()

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
    
    async def chat(self, message: str, file: dict | None = None) -> AsyncGenerator[str, None]:
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
        run_response = await self.agent.arun(messages, stream=True)
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
                message=message,
                response=full_response
            )
            session.add(msg)
            session.commit()