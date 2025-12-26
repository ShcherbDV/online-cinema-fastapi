from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.dependencies import get_settings

settings = get_settings()

POSTGRESQL_DATABASE_URL_SYNC = (
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_DB_PORT}/{settings.POSTGRES_DB}"
)

engine = create_engine(POSTGRESQL_DATABASE_URL_SYNC)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
