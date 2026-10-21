# GitHub presentation checklist

## Before you publish

1. Create the repository on GitHub, e.g. `cms-claims-anomaly-mlops`.
2. Keep `data/raw`, `data/processed`, `artifacts`, local MLflow DB files, and downloaded CMS ZIP/CSV files out of Git.
3. Run the project from a clean virtual environment.
4. Confirm `pytest -q` passes.
5. Confirm the GitHub Actions workflow turns green after push.
6. Run the MLflow UI locally and take one screenshot only if you want to add it to `docs/images`.

## Recommended real commit sequence

Make these commits as you actually complete the work; do not backdate or fabricate history.

```text
chore: scaffold cms claims portfolio project
feat: add claims ingestion validation and cleaning
feat: add SQL provider feature pipeline
feat: add provider anomaly screening model
feat: add supervised high-cost claim baseline
feat: track experiments and models with MLflow
chore: containerize pipeline with Docker
ci: add lint tests and smoke pipeline
 docs: add architecture limitations and interview walkthrough
```

## Commands to publish

```bash
git init
git add .
git commit -m "chore: scaffold cms claims portfolio project"
git branch -M main
git remote add origin <YOUR-GITHUB-REPO-URL>
git push -u origin main
```

## What to pin on the repository homepage

- A concise first paragraph explaining the CMS/program-integrity motivation.
- The architecture diagram near the top.
- The provider anomaly chart.
- A visible warning that anomaly != fraud.
- Quick-start commands that work.
- A short production mapping to AWS/Databricks.

## Five-minute live demo order

1. `README.md` - problem and architecture.
2. `src/cms_claims/transform.py` - ETL and data quality.
3. `sql/provider_features.sql` - SQL and feature engineering.
4. `src/cms_claims/anomaly.py` - unsupervised model and interpretability.
5. `artifacts/top_provider_anomalies.csv` - result ranking.
6. MLflow UI - parameters, metrics, artifacts, model version.
7. `.github/workflows/ci.yml` - reproducibility and CI.
8. `Dockerfile` and `docs/ARCHITECTURE.md` - container/cloud extension.
