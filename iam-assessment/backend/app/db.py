import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://iam:iam@db:5432/iam",
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

