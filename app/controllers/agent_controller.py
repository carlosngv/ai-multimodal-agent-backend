from blacksheep import Request, Response, StreamedContent
from blacksheep.server.controllers import Controller, get, post
from app.services.openrouter_service import OpenRouterService




class AgentController(Controller):
    
    @post('/chat')
    async def chat(self, request: Request, openrouter_service: OpenRouterService):
        data = await request.json()
        
        # ? Obtener el generator con el contenido de los chunks
        response_generator = openrouter_service.chat(data["message"])
        
        # ? Codificar los chunks, es el formato que acepta el StreamedContent Response de Blacksheep
        async def provider():
            async for chunk in response_generator:
                if chunk:
                    yield chunk.encode("utf-8")

        return Response(
            200,
            content=StreamedContent(
                b"text/plain",
                provider
            )
        )