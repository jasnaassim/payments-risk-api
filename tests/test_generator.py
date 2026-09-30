from scripts.generate_transactions import generate


def test_generation_is_deterministic():
    assert generate(100, 10, 7, seed=1) == generate(100, 10, 7, seed=1)


def test_disputes_only_on_succeeded_payments():
    rows = generate(5000, 50, 30, seed=7)
    assert all(r["status"] == "succeeded" for r in rows if r["is_disputed"] == "true")


def test_risk_scores_in_range():
    rows = generate(2000, 20, 30, seed=3)
    assert all(0 <= r["risk_score"] <= 100 for r in rows)
