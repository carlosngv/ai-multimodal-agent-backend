from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_key: str
    postgres_user: str
    postgres_password: str
    environment: str
    openrouter_base_url: str
    
    class Config:
        env_file=".env"