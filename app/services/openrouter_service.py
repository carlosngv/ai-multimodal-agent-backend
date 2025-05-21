
from typing import Any, AsyncGenerator
from app.config.settings import Settings

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

class OpenRouterService:
    settings = Settings()
    
    def __init__(self):
        
        try:
            self.agent = Agent(
                model=OpenAIChat(id="qwen/qwen2.5-vl-32b-instruct:free", api_key=self.settings.openrouter_key, base_url=self.settings.openrouter_base_url),
            )
        except ValueError as e:
            print(e)
            
    async def chat(self, message: str) -> AsyncGenerator[str, None]:
        run_response = await self.agent.arun(message, stream=True)
        async for chunk in run_response:
            if chunk.content:
                yield chunk.content