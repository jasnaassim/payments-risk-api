from datetime import date

from pydantic import BaseModel


class MerchantRisk(BaseModel):
    merchant_id: str
    merchant_category: str
    txn_count: int
    gross_volume_usd: float
    decline_rate: float
    dispute_rate: float | None
    avg_risk_score: float
    first_seen: date
    last_seen: date
    is_high_risk: bool


class DailyMetric(BaseModel):
    metric_date: date
    txn_count: int
    gross_volume_usd: float
    decline_rate: float
    dispute_rate: float | None


class Health(BaseModel):
    status: str
    backend: str
