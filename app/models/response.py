from pydantic import BaseModel

class ResponseOutput(BaseModel):
    summary: str
    keywords: list[str]