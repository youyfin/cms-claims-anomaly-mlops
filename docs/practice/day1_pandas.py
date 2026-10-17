"""
This script is day 1 - panda practice
"""

import pandas as pd


# --------------------------------------------------
# 1. Load
# --------------------------------------------------
print("\n")
print("---------1. LOAD--------------------------------\n")
df = pd.read_csv("data/raw/inpatient_claims.csv")

print("Shape:")
print(df.shape)

print("\nHead:")
print(df.head())

print("\nInfo:")
df.info()


# --------------------------------------------------
# 2. Select
# --------------------------------------------------

print("\n")
print("---------2. SELECT--------------------------------\n")

high_payment_claims = df.loc[df["CLM_PMT_AMT"] > 10_000, ["CLM_ID", "PRVDR_NUM", "CLM_PMT_AMT"]]

print("\nHigh-payment claims:")
print(high_payment_claims.head(10))


# --------------------------------------------------
# 3. Missing values
# --------------------------------------------------

print("\n")
print("---------3. MISSING VALUES--------------------------------\n")

missing_counts = df.isna().sum().sort_values(ascending=False)

print("\nMissing values:")
print(missing_counts.head(15))


# --------------------------------------------------
# 4. Datetime
# --------------------------------------------------

print("\n")
print("---------4. DATETIME--------------------------------\n")

df_dates = df.copy()

df_dates["CLM_FROM_DT"] = pd.to_datetime(
    df_dates["CLM_FROM_DT"],
    format="%Y%m%d",
    errors="coerce",
)

print("\nParsed dates:")
print(df_dates["CLM_FROM_DT"].head())


# --------------------------------------------------
# 5. GroupBy
# --------------------------------------------------

print("\n")
print("---------5. GROUPBY--------------------------------\n")

provider_claim_count = df.groupby("PRVDR_NUM").size().sort_values(ascending=False)

print("\nTop providers by claim count:")
print(provider_claim_count.head(10))


# --------------------------------------------------
# 6. Aggregate
# --------------------------------------------------

print("\n")
print("---------6. AGGREGATE--------------------------------\n")

provider_summary = (
    df.groupby("PRVDR_NUM").agg(
        claim_count=("CLM_ID","count",),
        unique_beneficiaries=("DESYNPUF_ID", "nunique"),
        total_payment=("CLM_PMT_AMT", "sum"),
        avg_payment=("CLM_PMT_AMT", "mean"),
        max_payment=("CLM_PMT_AMT", "max"),
        avg_utilization_days=("CLM_UTLZTN_DAY_CNT", "mean"),).reset_index())

print("\nProvider summary:")
print(provider_summary.sort_values("avg_payment", ascending=False).head(10))


# --------------------------------------------------
# 7. Merge
# --------------------------------------------------

print("\n")
print("---------7. MERGE--------------------------------\n")

provider_lookup = pd.DataFrame(
    {
        "PRVDR_NUM": [
            "P0115",
            "P0116",
            "P0117",
        ],
        "review_group": [
            "A",
            "A",
            "B",
        ],
    }
)

merged = df.merge(
    provider_lookup,
    on="PRVDR_NUM",
    how="left",
)

print("\nMerged sample:")
print(
    merged[
        [
            "CLM_ID",
            "PRVDR_NUM",
            "CLM_PMT_AMT",
            "review_group",
        ]
    ].head(20)
)