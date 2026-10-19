from __future__ import annotations

import json
from pathlib import Path

from .anomaly import train_anomaly_model
from .config import load_config, resolve_project_path
from .sql_features import build_provider_features
from .supervised import train_high_cost_classifier
from .transform import clean_claims


def run_pipeline(project_root: Path, config_path: Path, enable_mlflow: bool | None = None) -> dict:
    '''
    Ochestrator/Pipeline: Read configration-> path resolution -> clean_claims() -> build_provider_features() -> train_anomaly_model()
                 -> train_high_cost_classifier -> Save summary
    '''
    # Path Resolution
    cfg = load_config(config_path)                          # connection to config.yaml(config file -> dictionary)
    data_cfg = cfg["data"]
    project_cfg = cfg["project"]
    
    raw_csv = resolve_project_path(project_root, data_cfg["raw_csv"])                                  # raw data: 12000 rows
    cleaned_csv = resolve_project_path(project_root, data_cfg["cleaned_csv"])                          # cleaned data: 12000 rows (placeholder for the cleaned data)
    sqlite_db = resolve_project_path(project_root, data_cfg["sqlite_db"])                              # SQLite DB file to store tables: inpatient_claims, provider_features
    provider_features_csv = resolve_project_path(project_root, data_cfg["provider_features_csv"])      # provider_features: 120 rows
    sql_file = project_root / "sql" / "provider_features.sql"                                          # SQL file to build provider_features
    artifact_dir = project_root / "artifacts"                                                          
    
    # ETL pipeline: Extract -> Transform -> Load
    quality = clean_claims(                                                                            # clean the claims data and generate features for the raw claims data (12000 rows)
        raw_csv,
        cleaned_csv,
        high_cost_quantile=float(data_cfg["high_cost_quantile"]),
    )
    build_provider_features(cleaned_csv, sqlite_db, sql_file, provider_features_csv)                   # build provider_features: 120 rows
    
    # MLflow Configuration
    mlflow_base = cfg.get("mlflow", {}).copy()           
    if enable_mlflow is not None:                                                                      # enable_mlflow: True or False
        mlflow_base["enabled"] = enable_mlflow
    if "tracking_db" in mlflow_base:                             
        mlflow_base["tracking_db"] = str(resolve_project_path(project_root, mlflow_base["tracking_db"]))     # absolute path
    
    # Anomaly Model Training (Unsupervised)
    anomaly_mlflow = mlflow_base.copy()
    anomaly_mlflow["registered_model_name"] = mlflow_base.get("anomaly_registered_model")
    anomaly = train_anomaly_model(
        provider_features_csv=provider_features_csv,
        artifact_dir=artifact_dir,
        random_state=int(project_cfg["random_state"]),
        contamination=float(cfg["anomaly_model"]["contamination"]),
        n_estimators=int(cfg["anomaly_model"]["n_estimators"]),
        top_n=int(project_cfg["top_n_anomalies"]),
        mlflow_cfg=anomaly_mlflow,
    )

    # Supervised Model Training (Supervised)
    supervised_mlflow = mlflow_base.copy()
    supervised_mlflow["registered_model_name"] = mlflow_base.get("supervised_registered_model")
    supervised = train_high_cost_classifier(
        cleaned_csv=cleaned_csv,
        artifact_dir=artifact_dir,
        random_state=int(project_cfg["random_state"]),
        test_size=float(cfg["supervised_model"]["test_size"]),
        class_weight=str(cfg["supervised_model"]["class_weight"]),
        n_estimators=int(cfg["supervised_model"]["n_estimators"]),
        mlflow_cfg=supervised_mlflow,
    )
    
    # Save the summary
    summary = {
        "data_quality": quality,
        "anomaly_model": anomaly["metrics"],
        "supervised_model": supervised["metrics"],
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
