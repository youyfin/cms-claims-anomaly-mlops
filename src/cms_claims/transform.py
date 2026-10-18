from __future__ import annotations

from pathlib import Path

import pandas as pd

from .validation import data_quality_report, validate_raw_claims      # Input & Gatekeeping

DATE_COLUMNS = ["CLM_FROM_DT", "CLM_THRU_DT", "CLM_ADMSN_DT", "NCH_BENE_DSCHRG_DT"]
NUMERIC_COLUMNS = [
    "CLM_PMT_AMT",
    "NCH_PRMRY_PYR_CLM_PD_AMT",
    "CLM_PASS_THRU_PER_DIEM_AMT",
    "CLM_UTLZTN_DAY_CNT",
]


def _parse_cms_date(series: pd.Series) -> pd.Series:
    '''
    Parse CMS DE-SynPUF dates.
    '''
    # CMS DE-SynPUF dates are commonly stored as YYYYMMDD-like values.
    text = series.astype("string").str.replace(r"\.0$", "", regex=True).str.strip()
    return pd.to_datetime(text, format="%Y%m%d", errors="coerce")


def clean_claims(raw_csv: Path, output_csv: Path, high_cost_quantile: float = 0.90) -> dict:
    '''
    Clean the claims data and generate features for the raw claims data (12000 rows)
    '''
    df = pd.read_csv(raw_csv, dtype={"DESYNPUF_ID": "string", "CLM_ID": "string", "PRVDR_NUM": "string"})

    # Input & Gatekeeping
    validate_raw_claims(df)
    before = data_quality_report(df)

    # Data Cleaning:Drop duplicates and keep only valid providers
    df = df.drop_duplicates(subset=["CLM_ID"]).copy()     # keep = first occurrence
    df = df[df["PRVDR_NUM"].notna()].copy()

    # Data Cleaning: Parse CMS DE-SynPUF dates
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = _parse_cms_date(df[col])

    # Data Cleaning: Convert numeric columns to numeric
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)      # set missing values = 0

    if "CLM_ADMSN_DT" in df.columns:
        start = df["CLM_ADMSN_DT"].fillna(df["CLM_FROM_DT"])
    else:
        start = df["CLM_FROM_DT"]
    end = df.get("NCH_BENE_DSCHRG_DT", df["CLM_THRU_DT"])
    end = end.fillna(df["CLM_THRU_DT"])
    
    # Feature Engineering: length of stay, weekend start, diagnosis count, procedure count, primary payer zero, high cost claim
    df["length_of_stay"] = (end - start).dt.days.clip(lower=0).fillna(0)
    df["weekend_start"] = df["CLM_FROM_DT"].dt.dayofweek.isin([5, 6]).astype(int)         # Monday(0) - Sunday(6)

    diagnosis_cols = [c for c in df.columns if c.startswith("ICD9_DGNS_CD_")]
    procedure_cols = [c for c in df.columns if c.startswith("ICD9_PRCDR_CD_")]
    df["diagnosis_count"] = df[diagnosis_cols].notna().sum(axis=1) if diagnosis_cols else 0
    df["procedure_count"] = df[procedure_cols].notna().sum(axis=1) if procedure_cols else 0
    df["primary_payer_zero"] = (df["NCH_PRMRY_PYR_CLM_PD_AMT"] <= 0).astype(int)         #  primary payer <=0 (True = 1) |  0 otherwise

    threshold = float(df["CLM_PMT_AMT"].quantile(high_cost_quantile))
    df["is_high_cost_claim"] = (df["CLM_PMT_AMT"] >= threshold).astype(int)

    # SQLite stores datetimes as strings cleanly when writing from pandas.
    # Write the cleaned data to a CSV file
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, date_format="%Y-%m-%d")                            # Write the cleaned data to a CSV file

    after = data_quality_report(df)                                                       # Quality Check after cleaning
    return {"before": before, "after": after, "high_cost_threshold": threshold}           
