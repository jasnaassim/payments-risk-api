def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "backend": "duckdb"}


def test_high_risk_merchants_sorted_and_flagged(client):
    r = client.get("/merchants/high-risk", params={"limit": 10})
    assert r.status_code == 200
    rows = r.json()
    assert 0 < len(rows) <= 10
    assert all(m["is_high_risk"] for m in rows)
    rates = [m["dispute_rate"] for m in rows]
    assert rates == sorted(rates, reverse=True)


def test_merchant_lookup(client):
    r = client.get("/merchants/m_0001")
    assert r.status_code == 200
    body = r.json()
    assert body["merchant_id"] == "m_0001"
    assert 0 <= body["decline_rate"] <= 1


def test_unknown_merchant_returns_404(client):
    assert client.get("/merchants/m_9999").status_code == 404


def test_daily_metrics_date_filter(client):
    r = client.get("/metrics/daily", params={"start": "2026-01-10", "end": "2026-01-16"})
    assert r.status_code == 200
    days = [row["metric_date"] for row in r.json()]
    assert len(days) == 7
    assert days[0] == "2026-01-10" and days[-1] == "2026-01-16"


def test_daily_metrics_rejects_bad_range(client):
    r = client.get("/metrics/daily", params={"start": "2026-02-01", "end": "2026-01-01"})
    assert r.status_code == 422


def test_limit_validation(client):
    assert client.get("/merchants/high-risk", params={"limit": 0}).status_code == 422
