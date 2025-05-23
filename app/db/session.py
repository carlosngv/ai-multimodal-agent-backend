from app.config.settings import Settings

from sqlmodel import create_engine, Session

settings = Settings()

DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}"

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
