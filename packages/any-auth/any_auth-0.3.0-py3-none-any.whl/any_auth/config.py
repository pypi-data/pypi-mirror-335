import logging
import os
import pathlib
import re
import typing

import diskcache
import faker
import httpx
import pydantic
import redis
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: typing.Literal["development", "production", "test"] = pydantic.Field(
        default="development",
    )

    # Database
    DATABASE_URL: pydantic.SecretStr = pydantic.Field(
        default=pydantic.SecretStr("mongodb://localhost:27017")
    )
    CACHE_URL: pydantic.SecretStr | None = pydantic.Field(default=None)

    # JWT
    JWT_SECRET_KEY: pydantic.SecretStr = pydantic.Field(default=pydantic.SecretStr(""))
    JWT_ALGORITHM: typing.Literal["HS256"] = pydantic.Field(default="HS256")

    # Token Expiration
    TOKEN_EXPIRATION_TIME: int = pydantic.Field(
        default=15 * 60
    )  # 15 minutes in seconds
    REFRESH_TOKEN_EXPIRATION_TIME: int = pydantic.Field(
        default=7 * 24 * 60 * 60
    )  # 7 days in seconds

    # Google OAuth
    GOOGLE_CLIENT_ID: pydantic.SecretStr | None = pydantic.Field(default=None)
    GOOGLE_CLIENT_SECRET: pydantic.SecretStr | None = pydantic.Field(default=None)
    GOOGLE_REDIRECT_URI: pydantic.SecretStr | None = pydantic.Field(default=None)

    # SMTP
    SMTP_USERNAME: pydantic.SecretStr | None = pydantic.Field(default=None)
    SMTP_PASSWORD: pydantic.SecretStr | None = pydantic.Field(default=None)
    SMTP_FROM: pydantic.SecretStr | None = pydantic.Field(default=None)
    SMTP_PORT: int = pydantic.Field(default=587)
    SMTP_SERVER: pydantic.SecretStr | None = pydantic.Field(default=None)
    SMTP_STARTTLS: bool = pydantic.Field(default=True)
    SMTP_SSL_TLS: bool = pydantic.Field(default=False)
    SMTP_USE_CREDENTIALS: bool = pydantic.Field(default=True)

    # Class Vars
    fake: typing.ClassVar[faker.Faker] = faker.Faker()

    # Private
    _cache: diskcache.Cache | redis.Redis | None = None
    _local_cache: diskcache.Cache | None = None

    @classmethod
    def required_environment_variables(cls):
        return (
            "DATABASE_URL",
            "JWT_SECRET_KEY",
        )

    @classmethod
    def probe_required_environment_variables(cls) -> None:
        for env_var in cls.required_environment_variables():
            if os.getenv(env_var) is not None:
                continue
            # Try to match the env var name in case insensitive manner
            for env_var_candidate in os.environ.keys():
                if re.match(env_var, env_var_candidate, re.IGNORECASE):
                    continue
            logger.warning(f"Environment variable {env_var} is not set")

        return None

    @property
    def cache(self) -> diskcache.Cache | redis.Redis:
        if self._cache:
            return self._cache

        if self.CACHE_URL and self.CACHE_URL.get_secret_value().startswith("redis://"):
            _url = httpx.URL(self.CACHE_URL.get_secret_value())
            logger.info(
                "Initializing Redis cache: "
                + f"{_url.copy_with(username=None, password=None, query=None)}"
            )
            self._cache = redis.Redis(str(_url))
        else:
            _cache_path = pathlib.Path("./.cache").resolve()
            logger.info(f"Initializing DiskCache: {_cache_path}")
            self._cache = diskcache.Cache(_cache_path)

        return self._cache

    @property
    def local_cache(self) -> diskcache.Cache:
        if self._local_cache:
            return self._local_cache

        self._local_cache = diskcache.Cache("./.cache")
        return self._local_cache

    def is_google_oauth_configured(self) -> bool:
        return (
            self.GOOGLE_CLIENT_ID is not None
            and self.GOOGLE_CLIENT_SECRET is not None
            and self.GOOGLE_REDIRECT_URI is not None
        )

    def is_smtp_configured(self) -> bool:
        return (
            self.SMTP_USERNAME is not None
            and self.SMTP_PASSWORD is not None
            and self.SMTP_FROM is not None
            and self.SMTP_SERVER is not None
        )
