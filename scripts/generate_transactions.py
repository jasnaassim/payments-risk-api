"""Generate a deterministic, synthetic payments dataset.

A small share of merchants are "risky": they get more declines, disputes,
and higher risk scores, so the pipeline has a real signal to find.
"""
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

CATEGORIES = ["electronics", "travel", "apparel", "digital_goods", "food", "gaming"]
COUNTRIES = ["US", "GB", "DE", "IN", "BR", "CA", "FR", "JP"]
CARD_TYPES = ["visa", "mastercard", "amex", "discover"]
FIELDS = [
    "transaction_id", "merchant_id", "merchant_category", "country",
    "card_type", "amount_usd", "status", "is_disputed", "risk_score", "created_at",
]


def build_merchants(rng: random.Random, n: int) -> list[dict]:
    return [
        {
            "merchant_id": f"m_{i:04d}",
            "category": rng.choice(CATEGORIES),
            "risky": rng.random() < 0.08,
        }
        for i in range(1, n + 1)
    ]


def generate(rows: int, merchants: int, days: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    merchant_list = build_merchants(rng, merchants)
    start = datetime(2026, 1, 1)
    records = []
    for i in range(1, rows + 1):
        m = rng.choice(merchant_list)
        risky = m["risky"]
        decline_p = 0.15 if risky else 0.05
        roll = rng.random()
        if roll < decline_p:
            status = "declined"
        elif roll < decline_p + 0.03:
            status = "refunded"
        else:
            status = "succeeded"
        dispute_p = 0.025 if risky else 0.003
        is_disputed = status == "succeeded" and rng.random() < dispute_p
        base_risk = rng.gauss(65 if risky else 25, 12)
        records.append({
            "transaction_id": f"txn_{i:08d}",
            "merchant_id": m["merchant_id"],
            "merchant_category": m["category"],
            "country": rng.choice(COUNTRIES),
            "card_type": rng.choice(CARD_TYPES),
            "amount_usd": round(rng.lognormvariate(3.5, 1.0), 2),
            "status": status,
            "is_disputed": str(is_disputed).lower(),
            "risk_score": max(0, min(100, round(base_risk))),
            "created_at": (start + timedelta(seconds=rng.randint(0, days * 86400))).isoformat(sep=" "),
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--merchants", type=int, default=200)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/transactions.csv"))
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    records = generate(args.rows, args.merchants, args.days, args.seed)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records):,} rows to {args.out}")


if __name__ == "__main__":
    main()
