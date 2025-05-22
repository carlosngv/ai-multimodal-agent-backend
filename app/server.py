from blacksheep import Application, get, post, Request
from app.config.settings import Settings
from app.db.db import init_db
from app.services.openrouter_service import OpenRouterService
from app.services.knowledge_service import KnowledgeService


settings = Settings()
app = Application()
init_db()

app.services.add_scoped(OpenRouterService)
app.services.add_scoped(KnowledgeService)

print( settings.openrouter_key )
@get("/{test_parameter}")
def home( request: Request ):

    test_parameter = request.route_values["test_parameter"]
    
    return {
        "fromParameter": test_parameter
    }

@post("/")
async def examplePost(request: Request):
    data = await request.json()
    return { "dataReceived": data }