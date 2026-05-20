from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_enabled: bool = True
    db_type: str = "sqlite"
    sqlite_path: str = "./app.db"
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "app_db"
    db_user: str = "postgres"
    db_password: str = "postgres"

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), env_file_encoding="utf-8")

    @property
    def database_url(self) -> str | None:
        if not self.db_enabled:
            return None

        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"

        if self.db_type == "postgres":
            return (
                f"postgresql+psycopg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )

        raise ValueError(f"Unsupported DB_TYPE: {self.db_type}")


@lru_cache
def get_settings() -> Settings:
    return Settings()
