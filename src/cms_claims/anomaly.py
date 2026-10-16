from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ANOMALY_FEATURES = [
    "claim_count",
    "unique_beneficiaries",
    "total_payment",
    "avg_payment",
    "max_payment",
    "avg_utilization_days",
    "avg_length_of_stay",
    "weekend_start_share",
    "avg_diagnosis_count",
    "avg_procedure_count",
    "primary_payer_zero_share",
    "high_cost_claim_share",
    "claims_per_beneficiary",
    "active_months",
]


def _reason_codes(features: pd.DataFrame, top_k: int = 3) -> pd.DataFrame:
    numeric = features[ANOMALY_FEATURES].astype(float)
    med = numeric.median()
    mad = (numeric - med).abs().median().replace(0, 1.0)
    robust_z = (numeric - med).abs().div(1.4826 * mad)
    reasons = []
    for _, row in robust_z.iterrows():
        top = row.sort_values(ascending=False).head(top_k).index.tolist()
        reasons.append(top)
    out = pd.DataFrame(index=features.index)
    for i in range(top_k):
        out[f"reason_{i+1}"] = [r[i] for r in reasons]
    return out


def train_anomaly_model(
    provider_features_csv: Path,
    artifact_dir: Path,
    random_state: int,
    contamination: float,
    n_estimators: int,
    top_n: int,
    mlflow_cfg: dict | None = None,
) -> dict:
    df = pd.read_csv(provider_features_csv)
    X = df[ANOMALY_FEATURES].fillna(0.0).astype(float)

    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "isolation_forest",
                IsolationForest(
                    n_estimators=n_estimators,
                    contamination=contamination,
                    random_state=random_state,
                ),
            ),
        ]
    )
    model.fit(X)
    raw_score = model.decision_function(X)
    prediction = model.predict(X)

    scored = df.copy()
    scored["risk_score"] = -raw_score
    scored["is_anomaly"] = (prediction == -1).astype(int)
    scored = pd.concat([scored, _reason_codes(scored)], axis=1)
    scored = scored.sort_values("risk_score", ascending=False)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    scored_path = artifact_dir / "provider_risk_scores.csv"
    model_path = artifact_dir / "provider_anomaly_model.joblib"
    chart_path = artifact_dir / "provider_risk_scatter.png"
    top_path = artifact_dir / "top_provider_anomalies.csv"
    scored.to_csv(scored_path, index=False)
    scored.head(top_n).to_csv(top_path, index=False)
    joblib.dump(model, model_path)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    normal = scored[scored["is_anomaly"] == 0]
    anomaly = scored[scored["is_anomaly"] == 1]
    ax.scatter(normal["claim_count"], normal["avg_payment"], alpha=0.55, label="normal")
    ax.scatter(anomaly["claim_count"], anomaly["avg_payment"], alpha=0.9, label="flagged")
    ax.set_xlabel("Claims per provider")
    ax.set_ylabel("Average claim payment")
    ax.set_title("Provider anomaly screening (educational prototype)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)

    metrics = {
        "provider_count": int(len(scored)),
        "flagged_count": int(scored["is_anomaly"].sum()),
        "flagged_rate": float(scored["is_anomaly"].mean()),
        "mean_flagged_avg_payment": float(anomaly["avg_payment"].mean()) if not anomaly.empty else 0.0,
        "mean_normal_avg_payment": float(normal["avg_payment"].mean()) if not normal.empty else 0.0,
    }

    if mlflow_cfg and mlflow_cfg.get("enabled", False):
        from .mlflow_utils import setup_mlflow

        mlflow = setup_mlflow(Path(mlflow_cfg["tracking_db"]), mlflow_cfg["experiment_name"])
        with mlflow.start_run(run_name="provider-anomaly-isolation-forest"):
            mlflow.log_params(
                {
                    "model": "IsolationForest",
                    "n_estimators": n_estimators,
                    "contamination": contamination,
                    "random_state": random_state,
                    "feature_count": len(ANOMALY_FEATURES),
                }
            )
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(chart_path))
            mlflow.log_artifact(str(top_path))
            mlflow.sklearn.log_model(
                sk_model=model,
                name="provider_anomaly_model",
                input_example=X.head(5),
                registered_model_name=mlflow_cfg.get("registered_model_name"),
            )

    return {"metrics": metrics, "scored_path": scored_path, "model_path": model_path, "chart_path": chart_path}
