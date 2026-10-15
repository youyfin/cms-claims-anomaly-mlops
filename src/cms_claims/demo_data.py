from __future__ import annotations

import numpy as np
import pandas as pd


def make_demo(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Generating "provider_ids(120)" and "anomaly_providers (6)"
    provider_ids = [f"P{n:04d}" for n in range(1, 121)]
    anomaly_providers = set(provider_ids[-6:])

    # Generating "providers" based on prob: if 12000 inpatient claims,general providers(9912) and anomaly providers(2088)
    probs = np.ones(len(provider_ids), dtype=float)
    probs[-6:] = 4.0
    probs /= probs.sum()
    providers = rng.choice(provider_ids, size=rows, p=probs)
    
    # Generating: "beneficiaries(5000 - repeatable), "start(Start Date of Treatment/Hospitalization), 
    #             "util_days(length of hospital stay)", "payment(medical bill)"
    beneficiaries = [f"B{n:06d}" for n in rng.integers(1, 5000, size=rows)]
    start = pd.Timestamp("2008-01-01") + pd.to_timedelta(rng.integers(0, 1095, size=rows), unit="D")
    util_days = rng.poisson(4, size=rows) + 1
    payment = rng.gamma(shape=2.2, scale=2200, size=rows)

    # Adding anomaly data to the demo data
    is_anom = np.array([p in anomaly_providers for p in providers])
    payment = payment * np.where(is_anom, rng.uniform(1.8, 3.5, size=rows), 1.0)
    util_days = util_days + np.where(is_anom, rng.integers(2, 8, size=rows), 0)
    weekend_shift = np.where(is_anom, rng.integers(0, 3, size=rows), 0)
    start = start + pd.to_timedelta(weekend_shift, unit="D")
    thru = start + pd.to_timedelta(util_days, unit="D")

    df = pd.DataFrame(
        {
            "DESYNPUF_ID": beneficiaries,
            "CLM_ID": [f"C{n:09d}" for n in range(1, rows + 1)],
            "SEGMENT": 1,
            "CLM_FROM_DT": start.strftime("%Y%m%d"),                                          # Claim start date
            "CLM_THRU_DT": thru.strftime("%Y%m%d"),                                           # Claim end date
            "PRVDR_NUM": providers,
            "CLM_PMT_AMT": np.round(payment, 2),
            "NCH_PRMRY_PYR_CLM_PD_AMT": np.round(rng.gamma(1.2, 250, size=rows), 2),          # Primary insurer's share of the cost
            "CLM_ADMSN_DT": start.strftime("%Y%m%d"),                                         # Patient admission date
            "CLM_PASS_THRU_PER_DIEM_AMT": np.round(rng.gamma(1.1, 50, size=rows), 2),         # Additional payment for the hospital's operating costs and physician education
            "CLM_UTLZTN_DAY_CNT": util_days,
            "NCH_BENE_DSCHRG_DT": thru.strftime("%Y%m%d"),                                    # Patient discharge date
            "CLM_DRG_CD": rng.choice(["001", "039", "064", "194", "291", "470"], size=rows),  # Diagnosis Related Group
        }
    )

    # Disease Categories
    for i in range(1, 11):
        df[f"ICD9_DGNS_CD_{i}"] = rng.choice(
            ["4019", "25000", "4280", "41401", "V5869", None], size=rows
        )

    # Surgical Procedures
    for i in range(1, 7):
        df[f"ICD9_PRCDR_CD_{i}"] = rng.choice(["0066", "3607", "3893", "8856", None], size=rows)
    return df
