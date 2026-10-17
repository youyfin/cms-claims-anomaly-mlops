# Random Forest, Isolation Forest, Evalutation Metrics:Precision/Recall/Accuracy/F1/ROC-AUC vs PR-AUC




## Evaluation Metrics

### Confusion matrix

| | Actually Positive (1) | Actually Negative (0) |
|---|---|---|
| **Predicted Positive (1)** | TP | FP |
| **Predicted Negative (0)** | FN | TN |

 - 사기 = Positive (1),  정상 = Negative(0)
 - TP = 사기라고 predict 했는데 actually 사기
 - TN = 정상이라고 predict 했는데 actually 정상
 - FP = 사기라고 predict 했는데 actually 정상
 - FN = 정상이라고 predict 했는데 actually 사기  <- 가장 치명적인 오류
### Precision/Recall/F1

- Recall = $\frac{TP}{TP+FN}$: 전체 실제 사기건중 모델이 몇 %나 잡아냈는가? (FN을 줄이는 게 핵심) 

- Precision = $\frac{TP}{TP+FP}$: 사기라고 예측한 것 중 실제 사기 일 확률은 얼마인가? (FP를 줄이는 게 핵심)

- $F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$
    - 우리 Medicare 이상 탐지 파이프라인에서 "사기/고액 청구를 얼마나 놓치지 않고 잡으면서(Recall), 동시에 멀쩡한 병원을 억울하게 의심하는 오탐(Precision)을 얼마나 잘 억제했는가"를 종합 평가하는 균형 지표
    - F1은 Precision과 Recall 중 어느 한쪽이라도 0에 가깝게 낮아지면, 전체 점수를 가차 없이 0점으로 떨어뜨린다

- Model Selection: ROC-AUC vs PR-AUC 
    - 목적: 여러 모델 중 어떤 모델이 진짜와 가짜를 구분해내는 '기본 변별력(Discrimination Power)'이 더 뛰어난지 비교할 때 쓰는 대표 지표
    - ROC-AUC의 착시:
        - ROC-AUC의 계산 공식에는 정상 데이터를 맞힌 TN(True Negative) 개수가 분모로 크게 작용합니다.
        - 정상 데이터가 9,900건이나 되다 보니, 모델이 정상 청구를 사기로 잘못 지적하는 오탐(FP)을 500건이나 저질러도 분모(9,900)에 묻혀서 오탐률(FPR)이 매우 낮게 계산됩니다.
        - 그 결과, 모델 성능이 터무니없이 엉망이어도 ROC-AUC 점수는 0.90 이상으로 후하게 나올 수 있습니다.
    - PR-AUC의 솔직함:
        - PR-AUC는 공식 계산에서 TN(정상 데이터)을 아예 배제합니다.
        - 오직 우리가 진짜 잡고 싶어 하는 소수 클래스(사기 청구건, $TP$, $FP$, $FN$)에만 모든 화력을 집중합니다.
        - 따라서 쓸데없는 오탐(FP)이 많아지면 Precision이 떡락하면서 PR-AUC 점수가 가차 없이 폭락합니다. 
    - ROC-AUC vs PR-AUC 핵심 비교

| 구분 | ROC-AUC | PR-AUC |
|---|---|---|
| 관심 영역 | 전체 데이터 (정상 + 사기 모두 고려) | 오직 소수 클래스 (사기 청구건만 집중) |
| 정상 데이터(TN) 영향 | TN이 크면 점수가 부풀려짐 | TN을 완전히 무시함 |
| 찍기(Random) 기준선 | 항상 0.50 | 실제 양성 비율 (사기가 10%면 베이스라인은 0.10) |
| 주요 사용 시점 | 데이터 비율이 비슷하거나, 전반적 변별력 확인 시 | 데이터 불균형이 극심한 이상 탐지(Fraud) |



