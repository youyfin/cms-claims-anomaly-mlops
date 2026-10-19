# supervised.py: Train a high-cost claim classifier using a Random Forest
# cleaned claims -> (X, y): X = 7 predictors, y = high-cost indicator -> train/test split
#                -> Random Forest -> fit ->  prediction+ probability
#                -> metrics: precision, recall, f1, roc_auc, pr_auc -> save:model + plot + feature importance 

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

# 7 predictors from cleaned claims
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
    y = df["is_high_cost_claim"].astype(int)                    # 1 if high-cost claim, 0 otherwise

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,                                            # keep the same proportion of high-cost and low-cost claims in the training and test sets
    )
    model = RandomForestClassifier(
        n_estimators=n_estimators,                             # number of trees in the forest
        random_state=random_state,                             
        class_weight=class_weight,                             # give more weight to the minority class (high-cost claims)
        n_jobs=-1,
        min_samples_leaf=2,                                    # minimum number of samples required to be at a leaf node
    )
    model.fit(X_train, y_train)                                # fit the model to the training set
    pred = model.predict(X_test)                               # predict the class labels for the test set
    proba = model.predict_proba(X_test)[:, 1]                  # P(y=1|x): predict the probability of the positive class (high-cost claims)

    metrics = {
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "pr_auc": float(average_precision_score(y_test, proba)),
        "test_rows": len(y_test),
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / "high_cost_claim_classifier.joblib"              # placeholder for the model path
    cm_path = artifact_dir / "high_cost_confusion_matrix.png"                    # placeholder for the confusion matrix path
    importance_path = artifact_dir / "high_cost_feature_importance.csv"          # placeholder for the feature importance path
    joblib.dump(model, model_path)                                               # save the model to the model path
    
    # Plot the confusion matrix
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, colorbar=False)
    ax.set_title("High-cost claim classifier - confusion matrix")
    fig.tight_layout()
    fig.savefig(cm_path, dpi=150)
    plt.close(fig)

    # Calculate the feature importance
    importances = pd.DataFrame(
        {"feature": CLAIM_FEATURES, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    importances.to_csv(importance_path, index=False)

    # Log the metrics, artifacts, and model to MLflow
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
                skops_trusted_types=["sklearn.tree._tree.Tree"],
            )

    return {"metrics": metrics, "model_path": model_path, "cm_path": cm_path}
