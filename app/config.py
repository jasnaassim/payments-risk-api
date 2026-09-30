from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_backend: Literal["duckdb", "snowflake"] = "duckdb"
    analytics_schema: str = "analytics"

    duckdb_path: str = "data/local.duckdb"

    snowflake_account: str | None = None
    snowflake_user: str | None = None
    snowflake_password: str | None = None
    snowflake_role: str = "SYSADMIN"
    snowflake_warehouse: str = "RISK_WH"
    snowflake_database: str = "PAYMENTS_RISK"


@lru_cache
def get_settings() -> Settings:
    return Settings()
