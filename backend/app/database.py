from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()
DATABASE_URL = settings.database_url

engine = None
SessionLocal = None
Base = declarative_base()

if DATABASE_URL:
    connect_args = {"check_same_thread": False} if settings.db_type == "sqlite" else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def is_database_enabled() -> bool:
    return DATABASE_URL is not None


def check_database_connection() -> bool:
    if engine is None:
        return False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
