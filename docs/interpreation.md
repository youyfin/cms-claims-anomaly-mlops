# Interpretation of Anomaly and supervised

## Result
- summary.json
    - data_quality:
        - before: 
            - rows: 12000,
            - columns: 29,
            - duplicate_claim_ids: 0,
            - missing_provider_rate: 0.0,
            - missing_payment_rate: 0.0
    
        - after: 
            - rows: 12000,
            - columns: 35,
            - duplicate_claim_ids: 0,
            - missing_provider_rate: 0.0,
            - missing_payment_rate: 0.0
        
        - high_cost_threshold: 12123.02500000001
<br><br>

    - anomaly_model: 
        - provider_count: 120,
        - flagged_coun: 6,
        - flagged_rate: 0.05,
        - mean_flagged_avg_payment: 12750.708184987181,
        - mean_normal_avg_payment: 4792.6309786658585
  
    - supervised_model: 
        - precision: 0.2179054054054054,
        - recall: 0.43,
        - f1: 0.289237668161435,
        - roc_auc: 0.6841462962962963,
        - pr_auc: 0.20030804391987156,
        - test_rows: 3000
<br><br>

## Summary

- Our pipeline is designed with a 'two-track' approach to detect two distinct forms of healthcare fraud.
    - At the provider level—where no labeled data exists: We applied unsupervised learning (Isolation Forest) to generate a risk-based review queue, tailored to the capacity of the audit team (covering 5% of providers). The effectiveness of this outlier screening is evidenced by the fact that the average claim amount for the flagged providers ($12,750) was approximately 2.66 times higher than that of standard providers ($4,792).

    - Separately, at the individual claim level: We utilized a high-value claim threshold (the $12,123 quantile) to facilitate supervised learning (Random Forest) for assessing the legitimacy of specific claims."

## Q&A
Q1. Why did you split the system into two separate models instead of integrating them into one?
    
    - Ans: This is due to the diverse nature of fraudulent schemes. While one-off, high-value claims can be identified using a classifier that analyzes individual receipts, "organized or systematic fraud"—where perpetrators disguise hundreds of claims as small-value transactions—can only be detected by applying unsupervised learning to aggregated data at the provider (hospital) level.

Q2. The Precision (0.218) and PR-AUC (0.200) for the supervised model appear low; doesn't this represent a limitation?

    - Ans: These figures are influenced by class imbalance and the inherent limitations of using "high-cost" claims as a proxy label—since a high-cost claim does not automatically equate to fraud. Rather than focusing solely on the raw Precision score, we evaluate the model based on its PR-AUC improvement over random selection and its Recall (0.43), which ensures that high-risk cases are not overlooked. The model serves as an initial screening filter; we are currently exploring the integration of graph neural networks (GNNs) to help uncover previously undetected fraudulent activity. 
    
    - 프록시 라벨과 성능 지표 설명 (쉽게 풀어보기)
        - 파생 프록시 라벨(Proxy Label)'이란?
            - 의미: 진짜 사기 정답지(Ground Truth)가 없다 보니, 대신 "비싼 청구건(고액 청구)이 사기일 확률이 높겠지?"라고 임시로 정답지 역할을 할 가짜 라벨을 만들어 쓴 것입니다.
            - 한계: 명품을 많이 산 사람이 다 사치품 중독자가 아니듯, 정당한 대형 수술이나 난치병 치료도 당연히 '고액 청구'가 됩니다. 따라서 모델이 "고액 청구=위험"이라고 판단했을 때 실제로는 정상 치료인 경우가 많아 정밀도(Precision)가 낮게 나오는 것은 당연한 한계입니다.

        - Precision 대신 Recall(0.43)을 강조하는 이유
            - 1차 스크리닝 필터의 목적: 현장 심사관 입장에서는 "정상건이 몇 개 잘못 포함되어 같이 조사 대상에 오르는 것(False Positive)"보다 "진짜 사기꾼을 못 보고 놓쳐버리는 것(False Negative)"이 훨씬 더 치명적입니다.
            - 따라서 "일단 위험해 보이는 전체의 43%(Recall)를 놓치지 않고 1차 검수대에 올려놓았다"는 점이 실무적으로 훨씬 의미가 있습니다.

    -  GNN(그래프 신경망)은 이 문제를 어떻게 해결하는가?
        - 기존 모델이 데이터 개별 피처(Feature) 중심의 분석이었다면, GNN은 데이터 간의 관계망 구조(Relational Structure) 중심의 분석