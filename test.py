from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="google/gemma-3n-e4b-it:free", api_key="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", base_url="https://openrouter.ai/api/v1"),   
)

agent.print_response('HOlaaa', stream=True)