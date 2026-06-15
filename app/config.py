from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path

ENV_FILE_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_file=ENV_FILE_PATH,
        case_sensitive=False,
    )

    # Postgres
    PG_USERNAME: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_NAME: str
    PG_URL: str = ""

    # Celery broker/backend
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    REDIS_URL: str = "redis://redis:6379/0"

    # Telegram (Telethon)
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION: str = "anon"
    TELEGRAM_PUBLISH_CHANNEL: str = ""  

    # OpenAI
    OPENAI_API_KEY: str = ""

    @model_validator(mode="after")
    def build_pg_url(self) -> "Settings":
        self.PG_URL = (
            f"postgresql+asyncpg://{self.PG_USERNAME}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}/{self.PG_NAME}"
        )
        return self

settings = Settings()