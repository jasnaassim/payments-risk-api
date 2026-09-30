"""Database access behind one small interface.

The API talks to `Database.query()` only, so the same endpoints run on
Snowflake in production and on a local DuckDB file in development and CI.
"""
from typing import Any, Protocol

from app.config import Settings


class Database(Protocol):
    def query(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]: ...


class DuckDBDatabase:
    def __init__(self, path: str) -> None:
        import duckdb

        self._con = duckdb.connect(path, read_only=True)

    def query(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        cur = self._con.cursor()
        cur.execute(sql, params or [])
        cols = [d[0].lower() for d in cur.description]
        return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]


class SnowflakeDatabase:
    def __init__(self, settings: Settings) -> None:
        import snowflake.connector

        snowflake.connector.paramstyle = "qmark"
        self._con = snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            role=settings.snowflake_role,
            warehouse=settings.snowflake_warehouse,
            database=settings.snowflake_database,
        )

    def query(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        with self._con.cursor() as cur:
            cur.execute(sql, params or [])
            cols = [d[0].lower() for d in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]


def create_database(settings: Settings) -> Database:
    if settings.db_backend == "snowflake":
        return SnowflakeDatabase(settings)
    return DuckDBDatabase(settings.duckdb_path)
