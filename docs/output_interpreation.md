# Interpretation of Anomaly and supervised

## DATA Cleaning and 
- validation.py: raw data check!
    - validate_raw_claims(df): No output (OK)
    - data_quality_report(df)
        - rows: 66494, 
        - columns: 81, 
        - duplicate_claim_ids: 60, 
        - missing_provider_rate: 0.0, 
        - missing_payment_rate: 0.0

- transform.py: generating cleaned data
    - clean_claims(df) -> inpatient_claims_clean.csv: 66434x87

- sql_features.py: "group by" on provider level
    - build_provider_features(inpatient_claims_clean.csv): 2704x16
<br>

## ETL (Extract, Transform, Load)
- E: Extract: CMS, csv
- T: Transform: Pandas validation + cleaning + derived features
- L: Load: cleaned DataFrame -> SQLite (then claims -> provider)
- Description:ETL and ELT are not specific tools. The distinction is mainly whether transformation happens before or after loading into the target data platform. In my local prototype I clean the raw claims with Pandas before loading them into SQLite, so it is ETL-like. In a cloud lakehouse I would usually land the raw files first and transform them in Databricks, which is more ELT-like
<br>


## provider describe
- let "providers = provider_features.csv"
- providers.describe().T

| feature | count | mean | std | min | 25% | 50% | 75% | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| claim_count | 2704 | 24.57 | 47.15 | 1 | 4.00 | 10.00 | 24.00 | 837 |
| unique_beneficiaries | 2704 | 20.11 | 36.24 | 1 | 4.00 | 9.00 | 21.00 | 616 |
| total_payment | 2704 | 234011.92 | 453637.90 | 0 | 35000.00 | 90000.00 | 228000.00 | 7999100 |
| avg_payment | 2704 | 9488.27 | 4088.51 | 0 | 7333.33 | 9025.68 | 10740.11 | 57000 |
| max_payment | 2704 | 28674.33 | 17673.37 | 0 | 13000.00 | 25000.00 | 44000.00 | 57000 |
| avg_utilization_days | 2704 | 5.56 | 2.92 | 0 | 4.15 | 5.17 | 6.25 | 57 |
| total_utilization_days | 2704 | 135.75 | 264.01 | 0 | 20.00 | 54.00 | 134.00 | 4715 |
| avg_length_of_stay | 2704 | 5.68 | 2.63 | 0 | 4.33 | 5.33 | 6.43 | 35 |
| weekend_start_share | 2704 | 0.29 | 0.21 | 0 | 0.18 | 0.28 | 0.36 | 1 |
| avg_diagnosis_count | 2704 | 8.06 | 0.83 | 2 | 7.75 | 8.12 | 8.52 | 10 |
| avg_procedure_count | 2704 | 1.44 | 0.81 | 0 | 1.00 | 1.38 | 1.75 | 6 |
| primary_payer_zero_share | 2704 | 0.98 | 0.07 | 0 | 0.98 | 1.00 | 1.00 | 1 |
| high_cost_claim_share | 2704 | 0.10 | 0.13 | 0 | 0.00 | 0.08 | 0.14 | 1 |
| claims_per_beneficiary | 2704 | 1.15 | 0.25 | 1 | 1.00 | 1.04 | 1.22 | 5 |
| active_months | 2704 | 11.55 | 9.75 | 1 | 4.00 | 8.00 | 17.00 | 37 |

- total utilization_days: median (54) and mean (135.75) $\Rightarrow$ the distribution is right-skewed
- length of stay = physical stay period 
- avg_utilization_days = medicare claim days



## Result by pipeline (run_pipeline.py)
- summary.json
    - data_quality:
        - before: 
            - rows: 66494,
            - columns: 81,
            - duplicate_claim_ids: 60,
            - missing_provider_rate: 0.0,
            - missing_payment_rate: 0.0
    
        - after: 
            - rows: 66434,
            - columns: 87,
            - duplicate_claim_ids: 0,
            - missing_provider_rate: 0.0,
            - missing_payment_rate: 0.0
        
        - high_cost_threshold: 19000.0
<br><br>

    - anomaly_model: 
        - provider_count: 2704,
        - flagged_coun: 136,
        - flagged_rate: 0.05029585798816568,
        - mean_flagged_avg_payment: 15038.09692012271,
        - mean_normal_avg_payment: 9194.35112078898
  
    - supervised_model: 
        - precision: 0.26842930764060047,
        - recall: 0.6932870370370371,
        - f1: 0.3870134065579066,
        - roc_auc: 0.8017437371978187,
        - pr_auc: 0.3607486905647165,
        - test_rows: 16609 
<br><br>

## Summary

- Our pipeline is designed with a 'two-track' approach to detect two distinct forms of healthcare fraud.
    - At the provider level—where no labeled data exists: We applied unsupervised learning (Isolation Forest) to generate a risk-based review queue, tailored to the capacity of the audit team (covering about 5% of providers). The effectiveness of this outlier screening is evidenced by the fact that the average claim amount for the flagged providers ($15038) was approximately 1.63 times higher than that of standard providers ($9194).

    - Separately, at the individual claim level: We utilized a high-value claim threshold (the $19000 quantile) to facilitate supervised learning (Random Forest) for assessing the legitimacy of specific claims. We use train_data = 75% (49825), test data = 25% (16694) 

## Q&A
Q1. Why did you split the system into two separate models instead of integrating them into one?
    
    - Ans: This is due to the diverse nature of fraudulent schemes. While one-off, high-value claims can be identified using a classifier that analyzes individual receipts, "organized or systematic fraud"—where perpetrators disguise hundreds of claims as small-value transactions—can only be detected by applying unsupervised learning to aggregated data at the provider (hospital) level.

Q2. The Precision (0.268) and PR-AUC (0.3607) for the supervised model appear low; doesn't this represent a limitation?

    - Ans: These figures are influenced by class imbalance and the inherent limitations of using "high-cost" claims as a proxy label—since a high-cost claim does not automatically equate to fraud. Rather than focusing solely on the raw Precision score, we evaluate the model based on its PR-AUC improvement over random selection and its Recall (0.693), which ensures that high-risk cases are not overlooked. The model serves as an initial screening filter; we are currently exploring the integration of graph neural networks (GNNs) to help uncover previously undetected fraudulent activity. 
    
    - 프록시 라벨과 성능 지표 설명 (쉽게 풀어보기)
        - 파생 프록시 라벨(Proxy Label)'이란?
            - 의미: 진짜 사기 정답지(Ground Truth)가 없다 보니, 대신 "비싼 청구건(고액 청구)이 사기일 확률이 높겠지?"라고 임시로 정답지 역할을 할 가짜 라벨을 만들어 쓴 것입니다.
            - 한계: 명품을 많이 산 사람이 다 사치품 중독자가 아니듯, 정당한 대형 수술이나 난치병 치료도 당연히 '고액 청구'가 됩니다. 따라서 모델이 "고액 청구=위험"이라고 판단했을 때 실제로는 정상 치료인 경우가 많아 정밀도(Precision)가 낮게 나오는 것은 당연한 한계입니다.

        - Precision 대신 Recall(0.693)을 강조하는 이유
            - 1차 스크리닝 필터의 목적: 현장 심사관 입장에서는 "정상건이 몇 개 잘못 포함되어 같이 조사 대상에 오르는 것(False Positive)"보다 "진짜 사기꾼을 못 보고 놓쳐버리는 것(False Negative)"이 훨씬 더 치명적입니다.
            - 따라서 "일단 위험해 보이는 전체의 69%(Recall)를 놓치지 않고 1차 검수대에 올려놓았다"는 점이 실무적으로 훨씬 의미가 있습니다.

    -  GNN(그래프 신경망)은 이 문제를 어떻게 해결하는가?
        - 기존 모델이 데이터 개별 피처(Feature) 중심의 분석이었다면, GNN은 데이터 간의 관계망 구조(Relational Structure) 중심의 분석