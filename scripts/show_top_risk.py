#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path("artifacts/top_provider_anomalies.csv"))
    parser.add_argument("--n", type=int, default=10)
    args = parser.parse_args()
    df = pd.read_csv(args.file).head(args.n)
    cols = [
        "provider_id",
        "risk_score",
        "claim_count",
        "avg_payment",
        "high_cost_claim_share",
        "claims_per_beneficiary",
        "reason_1",
        "reason_2",
        "reason_3",
    ]
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
