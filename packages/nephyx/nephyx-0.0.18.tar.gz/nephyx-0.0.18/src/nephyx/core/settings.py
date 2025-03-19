from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict


class BaseSettings(PydanticBaseSettings):

    model_config = SettingsConfigDict(env_file=".env")

    database_host: str = "localhost"
    database_port: str = "5432"
    database_name: str
    database_user: str
    database_password: str
    database_url: PostgresDsn | None = None

    @field_validator("database_url")
    @classmethod
    def assemble_database_url(cls, v: PostgresDsn | None, values):
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=values.data.get("database_user"),
            password=values.data.get("database_password"),
            host=values.data.get("database_host"),
            port=int(values.data.get("database_port")),
            path=values.data.get("database_name"),
        )
