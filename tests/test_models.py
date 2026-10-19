from pathlib import Path

from cms_claims.anomaly import train_anomaly_model
from cms_claims.demo_data import make_demo
from cms_claims.sql_features import build_provider_features
from cms_claims.supervised import train_high_cost_classifier
from cms_claims.transform import clean_claims


def test_models_without_mlflow(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    clean = tmp_path / "clean.csv"
    db = tmp_path / "claims.db"
    features_csv = tmp_path / "provider.csv"
    artifacts = tmp_path / "artifacts"
    sql = Path(__file__).resolve().parents[1] / "sql" / "provider_features.sql"

    make_demo(2000, 42).to_csv(raw, index=False)
    clean_claims(raw, clean)
    build_provider_features(clean, db, sql, features_csv)
    anomaly = train_anomaly_model(features_csv, artifacts, 42, 0.05, 50, 10, mlflow_cfg=None)
    supervised = train_high_cost_classifier(clean, artifacts, 42, 0.25, "balanced", 50, mlflow_cfg=None)

    assert anomaly["metrics"]["provider_count"] > 20
    assert 0 < anomaly["metrics"]["flagged_rate"] < 0.2
    assert 0 <= supervised["metrics"]["pr_auc"] <= 1
