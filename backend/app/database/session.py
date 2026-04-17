from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings
from backend.app.database.base import Base

settings = get_settings()

engine = create_engine(
    settings.sqlalchemy_database_url,
    echo=settings.db_echo,
    future=True,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables() -> None:
    from backend.app.models import click, link  # noqa: F401

    Base.metadata.create_all(bind=engine)
