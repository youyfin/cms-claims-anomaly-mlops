from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

CLAIM_FEATURES = [
    "NCH_PRMRY_PYR_CLM_PD_AMT",
    "CLM_UTLZTN_DAY_CNT",
    "length_of_stay",
    "weekend_start",
    "diagnosis_count",
    "procedure_count",
    "primary_payer_zero",
]


def train_high_cost_classifier(
    cleaned_csv: Path,
    artifact_dir: Path,
    random_state: int,
    test_size: float,
    class_weight: str,
    n_estimators: int,
    mlflow_cfg: dict | None = None,
) -> dict:
    df = pd.read_csv(cleaned_csv)
    X = df[CLAIM_FEATURES].fillna(0.0).astype(float)
    y = df["is_high_cost_claim"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        class_weight=class_weight,
        n_jobs=-1,
        min_samples_leaf=2,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "pr_auc": float(average_precision_score(y_test, proba)),
        "test_rows": int(len(y_test)),
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / "high_cost_claim_classifier.joblib"
    cm_path = artifact_dir / "high_cost_confusion_matrix.png"
    importance_path = artifact_dir / "high_cost_feature_importance.csv"
    joblib.dump(model, model_path)

    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, colorbar=False)
    ax.set_title("High-cost claim classifier - confusion matrix")
    fig.tight_layout()
    fig.savefig(cm_path, dpi=150)
    plt.close(fig)

    importances = pd.DataFrame(
        {"feature": CLAIM_FEATURES, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    importances.to_csv(importance_path, index=False)

    if mlflow_cfg and mlflow_cfg.get("enabled", False):
        from .mlflow_utils import setup_mlflow

        mlflow = setup_mlflow(Path(mlflow_cfg["tracking_db"]), mlflow_cfg["experiment_name"])
        with mlflow.start_run(run_name="high-cost-claim-random-forest"):
            mlflow.log_params(
                {
                    "model": "RandomForestClassifier",
                    "n_estimators": n_estimators,
                    "class_weight": class_weight,
                    "random_state": random_state,
                    "test_size": test_size,
                }
            )
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(cm_path))
            mlflow.log_artifact(str(importance_path))
            mlflow.sklearn.log_model(
                sk_model=model,
                name="high_cost_claim_classifier",
                input_example=X_train.head(5),
                registered_model_name=mlflow_cfg.get("registered_model_name"),
            )

    return {"metrics": metrics, "model_path": model_path, "cm_path": cm_path}
