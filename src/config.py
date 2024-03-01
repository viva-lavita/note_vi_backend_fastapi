from typing import Optional

from pydantic import ValidationInfo
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class PostgresDBSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_ECHO: bool = False

    POSTGRES_URI: Optional[str] = None

    @field_validator("POSTGRES_URI")
    def assemble_db_connection(
        cls, v: Optional[str], values: ValidationInfo
    ) -> str:
        if isinstance(v, str):
            return v
        # Return URL-connect 'postgresql://postgres:password@localhost:5432/invoices'
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}?async_fallback=True".format(
            user=values.data["POSTGRES_USER"],
            password=values.data["POSTGRES_PASSWORD"],
            host=values.data["POSTGRES_HOST"],
            port=values.data["POSTGRES_PORT"],
            db=values.data["POSTGRES_DB"],
        )


class AuthSettings(BaseSettings):
    SECRET_AUTH_KEY: str
    ROLE_DEFAULT: str = "user"


class LoggerSettings(BaseSettings):
    LOGGER_CONSOLE: bool = False
    LOGGER_CONSOLE_LEVEL: str = "INFO"


settings = [
    PostgresDBSettings,
    AuthSettings,
    LoggerSettings
]


class AppSettings(*settings):
    PROJECT_NAME: str
    ENV: str
    API_PREFIX: str
    API_DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


config = AppSettings()
