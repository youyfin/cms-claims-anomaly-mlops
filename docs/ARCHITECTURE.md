# Architecture

```text
CMS DE-SynPUF inpatient CSV
        |
        v
[Ingestion + validation]
        |
        v
[Pandas cleaning / feature flags]
        |
        +------------------------------+
        |                              |
        v                              v
SQLite claims table              Claim-level features
        |                              |
        v                              v
SQL provider aggregation       RandomForest classifier
        |                              |
        v                              v
Provider feature table          PR-AUC / ROC-AUC / F1
        |
        v
Isolation Forest
        |
        v
Provider risk ranking + reason codes

Both model paths -> MLflow Tracking + Model Registry
Code -> Git/GitHub -> GitHub Actions CI
Runtime -> Docker container
```

## Why this architecture?

- **Pandas** demonstrates practical ETL/data cleaning.
- **SQLite + SQL** makes transformation logic inspectable and reproducible without requiring a cloud database.
- **Provider aggregation** mirrors a realistic program-integrity pattern: many claim-level events become provider-level behavioral features.
- **Isolation Forest** is appropriate when a trustworthy fraud label is unavailable.
- **Random Forest high-cost classifier** demonstrates supervised model evaluation separately; the target is *not* a fraud label.
- **MLflow** tracks parameters, metrics, artifacts, model versions, and lineage.
- **Docker + CI** make the project reproducible and testable.

## Production extension discussion

A production-oriented version could replace local components as follows:

| Local portfolio component | Production analog |
|---|---|
| CSV in `data/raw` | S3 / governed lakehouse storage |
| Pandas / SQLite | Spark + Delta / Databricks SQL |
| Local feature CSV | Feature Store / governed Delta feature table |
| Local MLflow SQLite backend | Databricks-managed MLflow / Unity Catalog model registry |
| `joblib` artifact | Registry-managed model artifact |
| Local batch score | Scheduled job or REST model serving |
| GitHub Actions | Enterprise CI/CD + approval gates |
| Docker | ECR + EKS/SageMaker/Databricks jobs depending on platform |
