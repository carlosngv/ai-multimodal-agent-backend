from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="google/gemma-3n-e4b-it:free", api_key="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", base_url="https://openrouter.ai/api/v1"),   
)

agent.print_response('HOlaaa')