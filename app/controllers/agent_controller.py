from blacksheep import Request, Response, StreamedContent
from blacksheep.server.controllers import Controller, post
from app.services.openrouter_service import OpenRouterService
from app.services.knowledge_service import KnowledgeService
from app.services.mcp_service import MCPService




class AgentController(Controller):
    
    @post('/chat')
    async def chat(self, request: Request, openrouter_service: OpenRouterService, knowledge_service: KnowledgeService):
        data = await request.json()
        
        file = None
        if 'file' in data:
            file = data['file']
        
        if ('type' in data) and data['type'] == "F":
            response_generator = knowledge_service.search(data["message"], data["citizen_email"])
        else:
            # ? Obtener el generator con el contenido de los chunks
            response_generator = openrouter_service.chat(data["message"], data["citizen_email"], file)
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
        
    @post('/mcp/chat')
    async def faqsChat(self, request: Request, mcp_service: MCPService):
        data = await request.json()
        req_type = data['type']
        response = "[NO HAY RESULTADOS]"
        if req_type == "S":
            response = await mcp_service.chat(data["message"], data["citizen_email"])
        elif req_type == "A":
            response = await mcp_service.locate_attractions(data["message"], data["citizen_email"])
        else:
            return {
                "response": response
            }
        return {
            "response": response
        }

        