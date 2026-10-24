#!/usr/bin/env python
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import requests

CMS_SAMPLE2_INPATIENT_URL = (
    "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/"
    "synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_2.zip"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CMS DE-SynPUF inpatient sample 2.")
    parser.add_argument("--url", default=CMS_SAMPLE2_INPATIENT_URL)
    parser.add_argument("--output", type=Path, default=Path("data/raw/inpatient_claims.csv"))
    args = parser.parse_args()                                                  # arg.url: CMS_SAMPLE2_INPATIENT_URL, arg.output: Path("data/raw/inpatient_claims.csv")

    print("Downloading official CMS DE-SynPUF file...")
    response = requests.get(args.url, timeout=120)                              # zip bytes file download
    response.raise_for_status()                                                 # raise for status: 400, 500, etc.
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:                   # zipfile.ZipFile: zip file object
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError("No CSV found inside CMS ZIP archive.")
        if len(csv_names) > 1:
            print(f"Multiple CSVs found; using {csv_names[0]}")
        args.output.parent.mkdir(parents=True, exist_ok=True)                    # create parent directory if not exists
        with zf.open(csv_names[0]) as src, args.output.open("wb") as dst:        # src: zip file object, dst: file object
            dst.write(src.read())                                                # write to file
    print(f"Saved CMS data to {args.output}")


if __name__ == "__main__":
    main()
