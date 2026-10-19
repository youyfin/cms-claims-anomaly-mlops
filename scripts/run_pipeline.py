#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cms_claims.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the end-to-end CMS claims ML pipeline.")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    parser.add_argument("--disable-mlflow", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]                                      # project root: PROJECTS/MLOps_demos/cms-claims-anomaly-mlops
    summary = run_pipeline(root, root / args.config, enable_mlflow=not args.disable_mlflow)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
