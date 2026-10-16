# Detailed Description

## Raw Data (inpatient_claims.csv): 12000x29

- 1. Billing Statement and Patient/Hospital Identification Information
    - DESYNPUF_ID: Patient ID
    - CLM_ID: claim ID
    - SEGMENT 
    - PRVDR_NUM: Provider Number/Identification

- 2. Date and Duration Information
    - CLM_FROM_DT: claim from:YYYYMMDD format
    - CLM_THRU_DT: claim end:YYYYMMDD format
        - For example, will billing start abruptly on a monthly basis after 3 months (e.g., 1/1 - 1/31, 2/1 - 2/28, 3/1 - 3/31)? In this case, if billing starts after 1/31
    
    - CLM_ADMSN_DT: Actual hospital admission date: Usually the same as CLM_FROM_DT
    - NCH_BENE_DSCHRG_DT: Actual patient discharge date,usually the same as CLM_THRU_DT
    - CLM_UTLZTN_DAY_CNT (Length of Hospital Stay: thru-start)

- 3. Payment of Medical Service  
    - CLM_PMT_AMT: Claim Payment Amount
    - NCH_PRMRY_PYR_CLM_PD_AMT:Primary insurer payment
        - An amount paid by a private primary insurer (or similar entity) prior to the Medicare claim, in addition to Medicare coverage. 
    - CLM_PASS_THRU_PER_DIEM_AMT
        - A daily subsidy provided by the government in addition to actual treatment or surgery costs, calculated based on the number of days a patient is hospitalized, to help cover expenses related to hospital operations and physician training.

- 4. Claim Diagnoiss Related Group
    - CLM_DRG_CD: Diagnostic Related Group


- 5. Additional Diagnostic Code - claim's clinical information
    - ICD9_DGNS_CD : 10 diagnosis codes
    - ICD9_PRCDR_CD : 6 procedure codes
<br><br>

## Cleaned claims data (inpatient_claims_clean.csv): 12000x35

- 1. Billing Statement and Patient/Hospital Identification Information
    - DESYNPUF_ID 
    - CLM_ID 
    - SEGMENT 
    - PRVDR_NUM 

- 2. Date and Duration Information
    - CLM_FROM_DT 
    - CLM_THRU_DT 
    - CLM_ADMSN_DT 
    - NCH_BENE_DSCHRG_DT 
    - CLM_UTLZTN_DAY_CNT

- 3. Payment of Medical Service 
    - CLM_PMT_AMT 
    - NCH_PRMRY_PYR_CLM_PD_AMT 
    - CLM_PASS_THRU_PER_DIEM_AMT 


- 4. Claim Diagnoiss Related Group
    - CLM_DRG_CD 

- 5. Additional Diagnostic Code - claim's clinical information
    - ICD9_DGNS_CD
        - 'ICD9_DGNS_CD_1' 'ICD9_DGNS_CD_2' 'ICD9_DGNS_CD_3' ... 'ICD9_DGNS_CD_9' 'ICD9_DGNS_CD_10'
    - ICD9_PRCDR_CD 
        - 'ICD9_PRCDR_CD_1' 'ICD9_PRCDR_CD_2' ... 'ICD9_PRCDR_CD_6'
 
- 6. Added features
    - length_of_stay = CLM_THRU_DT - CLM_FROM_DT 
    - weekend_start: CLM_FROM_DT = Saturday or Sunday $\Rightarrow$ 1, otherwise 0
    - diagnosis_count: Total number of diagnosis 
        - The total count of non-null columns among the 10 diagnosis code columns (ICD9_DGNS_CD_1 through ICD9_DGNS_CD_10); a value between 1 and 10 
    - procedure_count: Total number of procedure
        - The total number of non-null columns among the six columns from ICD9_PRCDR_CD_1 to ICD9_PRCDR_CD_6 (a value between 0 and 6).
    - primary_payer_zero: NCH_PRMRY_PYR_CLM_PD_AMT = 0 $\Rightarrow$  1, otherwise 0
    - is_high_cost_claim
        - 1 if CLM_PMT_AMT (claim payment amount) exceeds the top N% of the entire dataset (e.g., 0.90 or 0.95 quantile); otherwise, 0.
<br><br>

## Provider Features (provider_features.csv): 120x16
1. Description: By "Group by", it is categorized by provider. Then created the group (provider) features to compare providers

2. Features

- Basic Hospital Information and Activity Indicators
    - provider_id: PRVDR_NUM
    - claim_count: COUNT(CLM_ID)
    - unique_beneficiaries: COUNT(DISTINCT DESYNPUF_ID)
    - claims_per_beneficiary: claim_count / unique_beneficiaries
    - active_months:COUNT(DISTINCT strftime('%Y-%m', CLM_FROM_DT))

- Summary of Financial and Payment Data
    - total_payment: SUM(CLM_PMT_AMT)
    - avg_payment: AVG(CLM_PMT_AMT)
    - max_payment: MAX(CLM_PMT_AMT)

- Hospitalization period and days subject to fee application
    - avg_utilization_days: AVG(CLM_UTLZTN_DAY_CNT)
    - total_utilization_days: SUM(CLM_UTLZTN_DAY_CNT)
    - avg_length_of_stay: AVG(length_of_stay)

- Indicators of clinical practice and billing behavior patterns (ratios/averages)
    - weekend_start_share: SUM(weekend_start) / claim_count
    - avg_diagnosis_count: AVG(diagnosis_count)
    - avg_procedure_count: AVG(procedure_count)
    - primary_payer_zero_share: SUM(primary_payer_zero) / claim_count
    - high_cost_claim_share: SUM(is_high_cost_claim) / claim_count
       
