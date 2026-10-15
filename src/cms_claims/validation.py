from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {
    "DESYNPUF_ID",
    "CLM_ID",
    "CLM_FROM_DT",
    "CLM_THRU_DT",
    "PRVDR_NUM",
    "CLM_PMT_AMT",
    "NCH_PRMRY_PYR_CLM_PD_AMT",
    "CLM_UTLZTN_DAY_CNT",
}


def validate_raw_claims(df: pd.DataFrame) -> None:
    '''
    Check for the required columns and that the dataframe is not empty.
    '''
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Missing required CMS columns: {missing}")
    if df.empty:
        raise ValueError("Input claims file is empty.")


def data_quality_report(df: pd.DataFrame) -> dict[str, float | int]:
    '''
    Generate a report on the data quality of the claims data.
    '''
    duplicate_claims = int(df.duplicated(subset=["CLM_ID"]).sum())
    missing_provider = float(df["PRVDR_NUM"].isna().mean())
    missing_payment = float(df["CLM_PMT_AMT"].isna().mean())
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "duplicate_claim_ids": duplicate_claims,
        "missing_provider_rate": missing_provider,
        "missing_payment_rate": missing_payment,
    }
