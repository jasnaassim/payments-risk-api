from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request

from app.config import get_settings
from app.db import Database, create_database
from app.schemas import DailyMetric, Health, MerchantRisk


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = create_database(get_settings())
    yield


app = FastAPI(
    title="Payments Risk API",
    description="Merchant risk metrics built with Snowflake, dbt and FastAPI.",
    version="0.1.0",
    lifespan=lifespan,
)


def get_db(request: Request) -> Database:
    return request.app.state.db


DB = Annotated[Database, Depends(get_db)]


def table(name: str) -> str:
    # Schema comes from trusted config, never from user input.
    return f"{get_settings().analytics_schema}.{name}"


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", backend=get_settings().db_backend)


# Declared before /merchants/{merchant_id} so "high-risk" is not read as an id.
@app.get("/merchants/high-risk", response_model=list[MerchantRisk])
def high_risk_merchants(
    db: DB,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> list[dict]:
    return db.query(
        f"select * from {table('dim_merchant_risk')} "
        "where is_high_risk order by dispute_rate desc, merchant_id limit ?",
        [limit],
    )


@app.get("/merchants/{merchant_id}", response_model=MerchantRisk)
def merchant_risk(merchant_id: str, db: DB) -> dict:
    rows = db.query(
        f"select * from {table('dim_merchant_risk')} where merchant_id = ?",
        [merchant_id],
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found")
    return rows[0]


@app.get("/metrics/daily", response_model=list[DailyMetric])
def daily_metrics(
    db: DB,
    start: date | None = None,
    end: date | None = None,
    merchant_id: str | None = None,
) -> list[dict]:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must be on or before end")

    where, params = [], []
    if start:
        where.append("metric_date >= ?")
        params.append(start)
    if end:
        where.append("metric_date <= ?")
        params.append(end)
    if merchant_id:
        where.append("merchant_id = ?")
        params.append(merchant_id)
    where_sql = f"where {' and '.join(where)}" if where else ""

    return db.query(
        f"""
        select
            metric_date,
            sum(txn_count)                                  as txn_count,
            sum(gross_volume_usd)                           as gross_volume_usd,
            sum(declined_count) * 1.0 / sum(txn_count)      as decline_rate,
            sum(disputed_count) * 1.0
                / nullif(sum(succeeded_count), 0)           as dispute_rate
        from {table('fct_daily_merchant_metrics')}
        {where_sql}
        group by metric_date
        order by metric_date
        """,
        params,
    )
