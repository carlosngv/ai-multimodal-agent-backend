from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_key: str
    postgres_user: str
    postgres_password: str
    environment: str
    openrouter_base_url: str
    postgres_db: str
    google_maps_api_key: str
    gemini_key: str
    
    class Config:
        env_file=".env"