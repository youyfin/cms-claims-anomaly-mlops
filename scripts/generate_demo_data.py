#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from cms_claims.demo_data import make_demo


def main() -> None:
    '''
    Generate a small CMS-shaped demo fixture for local/CI use.                      # make_demo: Synthetic data generator, ex: df = make_demo(12000, 42)
    Args:
        rows: number of rows to generate
        seed: random seed
        output: path to save the output file
    Returns:
        None
    '''
    parser = argparse.ArgumentParser(description="Generate a small CMS-shaped demo fixture for local/CI use.")
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/raw/inpatient_claims.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = make_demo(args.rows, args.seed)                       # make_demo: Synthetic data generator, ex: df = make_demo(12000, 42)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} demo rows to {args.output}")


if __name__ == "__main__":
    main()