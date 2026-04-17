from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "D3 Links"
    app_env: str = "development"
    base_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///./backend/d3_links.db"
    db_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url.strip()

        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)

        if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
            return url.replace("postgresql://", "postgresql+psycopg://", 1)

        return url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
