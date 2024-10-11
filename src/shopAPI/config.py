from typing import Any, Optional
from pydantic import Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    VERSION: str = Field("0.0.1", json_schema_extra={"env": "VERSION"})
    PROJECT_NAME: str = Field("ShopAPI", json_schema_extra={"env": "PROJECT_NAME"})
    APP_HOST: str = Field("0.0.0.0", json_schema_extra={"env": "APP_HOST"})
    APP_PORT: str = Field("8000", json_schema_extra={"env": "APP_PORT"})
    DB_USER: str = Field("postgres", json_schema_extra={"env": "DB_USER"})
    DB_PASSWORD: str = Field("postgres", json_schema_extra={"env": "DB_PASSWORD"})
    DB_NAME: str = Field("postgres", json_schema_extra={"env": "DB_NAME"})
    DB_HOST: str = Field("localhost", json_schema_extra={"env": "DB_HOST"})
    DB_PORT: int | str = Field("5432", json_schema_extra={"env": "DB_PORT"})
    DB_ECHO: bool = Field(False, json_schema_extra={"env": "DB_ECHO"})
    DB_POOL_SIZE: int = Field(5, json_schema_extra={"env": "DB_POOL_SIZE"})
    DB_URI: Optional[PostgresDsn] = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    @field_validator("DB_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("DB_USER"),
            password=info.data.get("DB_PASSWORD"),
            host=info.data.get("DB_HOST"),
            port=int(info.data.get("DB_PORT")),
            path=info.data.get("DB_NAME"),
        )


settings = Settings()
