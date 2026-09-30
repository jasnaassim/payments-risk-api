"""Load the generated CSV into a local DuckDB file as raw.transactions.

This mirrors the Snowflake raw layer so dbt and the API run the same way
locally and in CI, with no cloud account needed.
"""
import argparse
import os
from pathlib import Path

import duckdb


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("data/transactions.csv"))
    parser.add_argument("--db", type=Path, default=Path(os.getenv("DUCKDB_PATH", "data/local.duckdb")))
    args = parser.parse_args()

    con = duckdb.connect(str(args.db))
    con.execute("create schema if not exists raw")
    con.execute(
        "create or replace table raw.transactions as "
        "select * from read_csv_auto(?, header = true)",
        [str(args.csv)],
    )
    count = con.execute("select count(*) from raw.transactions").fetchone()[0]
    print(f"Loaded {count:,} rows into {args.db} (raw.transactions)")
    con.close()


if __name__ == "__main__":
    main()
