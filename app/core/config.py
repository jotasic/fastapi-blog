# https://fastapi.tiangolo.com/advanced/settings/#pydantic-settings
import secrets
from typing import Literal

from fastapi_mail import ConnectionConfig
from pydantic import PostgresDsn, RedisDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["local", "prod"] = "local"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_TEST_DB: str = "test_database"
    API_V1_PREFIX: str = "/v1"

    JWT_SECRET_KEY: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: SecretStr

    @computed_field
    @property
    def EMAIL(self) -> ConnectionConfig:  # noqa: N802
        return ConnectionConfig(
            MAIL_USERNAME=self.SMTP_EMAIL,
            MAIL_PASSWORD=self.SMTP_PASSWORD,
            MAIL_PORT=self.SMTP_PORT,
            MAIL_SERVER=self.SMTP_HOST,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            MAIL_FROM="no-reply@test.com",
        )

    @computed_field
    @property
    def DATABASE_URI(self) -> str:  # noqa: N802
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ).encoded_string()

    @computed_field
    @property
    def DATABASE_TEST_URI(self) -> str:  # noqa: N802
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_TEST_DB,
        ).encoded_string()

    REDIS_USER_NAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_CACHE_DB: Literal["0", "1", "2"] = "0"

    @computed_field
    @property
    def CACHE_URI(self) -> str:  # noqa: N802
        return RedisDsn.build(
            scheme="redis",
            username=self.REDIS_USER_NAME,
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=self.REDIS_CACHE_DB,
        ).encoded_string()


settings = Settings()
