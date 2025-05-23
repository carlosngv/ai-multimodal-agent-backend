from blacksheep import Request, Response, StreamedContent
from blacksheep.server.controllers import Controller, post
from app.services.openrouter_service import OpenRouterService
from app.services.knowledge_service import KnowledgeService
from app.services.mcp_service import MCPService




class AgentController(Controller):
    
    @post('/chat')
    async def chat(self, request: Request, openrouter_service: OpenRouterService):
        data = await request.json()
        
        file = None
        if 'file' in data:
            file = data['file']
            
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
    @post('/faqs/chat')
    async def faqsChat(self, request: Request, knowledge_service: KnowledgeService):
        data = await request.json()
        response_generator = knowledge_service.search(data["message"], data["citizen_email"])
        
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
        response_generator = mcp_service.chat(data["message"], data["citizen_email"])
        
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
        
    @post('/mcp/chat-attractions')
    async def faqsChat(self, request: Request, mcp_service: MCPService):
        data = await request.json()
        response_generator = mcp_service.locate_attractions(data["message"], data["citizen_email"])
        
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