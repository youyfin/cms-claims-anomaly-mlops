from __future__ import annotations

from pathlib import Path


def setup_mlflow(tracking_db: Path, experiment_name: str):
    """Configure a local SQLite-backed MLflow Tracking + Registry store.

    Imported lazily so unit tests can run even when MLflow is not installed.
    """
    import mlflow

    tracking_db.parent.mkdir(parents=True, exist_ok=True)
    uri = f"sqlite:///{tracking_db.resolve().as_posix()}"
    mlflow.set_tracking_uri(uri)
    mlflow.set_registry_uri(uri)
    mlflow.set_experiment(experiment_name)
    return mlflow
