from typing import Any, Optional

from pydantic import ValidationInfo
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from src.constants import Environment


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
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}?async_fallback=True".format(
            user=values.data["POSTGRES_USER"],
            password=values.data["POSTGRES_PASSWORD"],
            host=values.data["POSTGRES_HOST"],
            port=values.data["POSTGRES_PORT"],
            db=values.data["POSTGRES_DB"],
        )


class TestPostgresDBSettings(BaseSettings):
    POSTGRES_USER_TEST: str = "test"
    POSTGRES_PASSWORD_TEST: str = "test"
    POSTGRES_HOST_TEST: str = "test_db"
    POSTGRES_PORT_TEST: int = 5433
    POSTGRES_DB_TEST: str = "test_db"
    POSTGRES_ECHO_TEST: bool = False

    POSTGRES_URI_TEST: Optional[str] = None

    @field_validator("POSTGRES_URI_TEST")
    def assemble_db_connection_test(
        cls, v: Optional[str], values: ValidationInfo
    ) -> str:
        if isinstance(v, str):
            return v
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}?async_fallback=True".format(
            user=values.data["POSTGRES_USER_TEST"],
            password=values.data["POSTGRES_PASSWORD_TEST"],
            host=values.data["POSTGRES_HOST_TEST"],
            port=values.data["POSTGRES_PORT_TEST"],
            db=values.data["POSTGRES_DB_TEST"],
        )


class AuthSettings(BaseSettings):
    SECRET_AUTH_KEY: str
    ROLE_DEFAULT: str = "user"


class LoggerSettings(BaseSettings):
    LOGGER_CONSOLE: bool = False
    LOGGER_CONSOLE_LEVEL: str = "INFO"


class EmailSettings(BaseSettings):
    EMAIL_HOST: str
    EMAIL_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str


class RedisSettings(BaseSettings):
    # REDIS_HOST: str
    # REDIS_PORT: int
    REDIS_URL: Optional[str] = None


settings = [
    PostgresDBSettings,
    TestPostgresDBSettings,
    AuthSettings,
    LoggerSettings,
    EmailSettings,
    RedisSettings
]


class AppSettings(*settings):
    PROJECT_NAME: str
    ENV: str
    APP_VERSION: str = "1"
    APP_URL: str
    ENVIRONMENT: Environment = Environment.TESTING
    API_DEBUG: bool = False

    class Config:
        case_sensitive = True


config = AppSettings()

app_configs: dict[str, Any] = {"title": "Note_vi_backend"}
if config.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/api/v{config.APP_VERSION}"

if not config.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
    app_configs["docs_url"] = None
    app_configs["redoc_url"] = None

if config.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = "/openapi.json"
    app_configs["docs_url"] = "/docs"
    app_configs["redoc_url"] = "/redoc"
