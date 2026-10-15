/*
    Build provider features from the cleaned claims data.
    i.e provider_wise summary features
*/

DROP TABLE IF EXISTS provider_features;

CREATE TABLE provider_features AS
SELECT
    PRVDR_NUM AS provider_id,
    COUNT(*) AS claim_count,
    COUNT(DISTINCT DESYNPUF_ID) AS unique_beneficiaries,
    SUM(CLM_PMT_AMT) AS total_payment,
    AVG(CLM_PMT_AMT) AS avg_payment,
    MAX(CLM_PMT_AMT) AS max_payment,
    AVG(CLM_UTLZTN_DAY_CNT) AS avg_utilization_days,
    SUM(CLM_UTLZTN_DAY_CNT) AS total_utilization_days,
    AVG(length_of_stay) AS avg_length_of_stay,
    AVG(weekend_start) AS weekend_start_share,
    AVG(diagnosis_count) AS avg_diagnosis_count,
    AVG(procedure_count) AS avg_procedure_count,
    AVG(primary_payer_zero) AS primary_payer_zero_share,
    AVG(is_high_cost_claim) AS high_cost_claim_share,
    1.0 * COUNT(*) / NULLIF(COUNT(DISTINCT DESYNPUF_ID), 0) AS claims_per_beneficiary,
    COUNT(DISTINCT substr(CLM_FROM_DT, 1, 7)) AS active_months
FROM inpatient_claims
GROUP BY PRVDR_NUM;
