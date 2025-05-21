from blacksheep import Application, get, post, Request

from app.config.settings import Settings

from app.services.openrouter_service import OpenRouterService

settings = Settings()
app = Application()

app.services.add_scoped(OpenRouterService)

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