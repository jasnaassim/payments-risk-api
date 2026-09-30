"""Build a small local warehouse once per test session.

Runs the same pipeline as production: generate -> load -> dbt build,
then points the API at the resulting DuckDB file.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def warehouse(tmp_path_factory) -> Path:
    tmp = tmp_path_factory.mktemp("warehouse")
    csv_path, db_path = tmp / "transactions.csv", tmp / "test.duckdb"
    env = {**os.environ, "DUCKDB_PATH": str(db_path), "DBT_TARGET": "local"}

    def run(cmd: list[str], cwd: Path = ROOT) -> None:
        subprocess.run(cmd, cwd=cwd, env=env, check=True, capture_output=True)

    # 40 merchants x ~125 txns each, so merchants clear the flagging minimum.
    run([
        sys.executable, "scripts/generate_transactions.py",
        "--rows", "5000", "--merchants", "40", "--out", str(csv_path),
    ])
    run([sys.executable, "scripts/load_local.py", "--csv", str(csv_path), "--db", str(db_path)])
    run(["dbt", "build", "--profiles-dir", "."], cwd=ROOT / "dbt")
    return db_path


@pytest.fixture(scope="session")
def client(warehouse: Path):
    os.environ["DB_BACKEND"] = "duckdb"
    os.environ["DUCKDB_PATH"] = str(warehouse)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
