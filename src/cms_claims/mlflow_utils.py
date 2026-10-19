from __future__ import annotations

from pathlib import Path


def setup_mlflow(tracking_db: Path, experiment_name: str):
    """
    - Configure a local SQLite-backed MLflow Tracking + Registry store.
    - runs, parameters, metrics, registered model metadata, model versions are stored in the tracking database.
    - Imported lazily so unit tests can run even when MLflow is not installed.
    """
    import mlflow

    tracking_db.parent.mkdir(parents=True, exist_ok=True)
    uri = f"sqlite:///{tracking_db.resolve().as_posix()}"        # resolve(): returns the absolute path of the tracking_db. as_posix(): .
    mlflow.set_tracking_uri(uri)                                 # runs/experiments: parameters, metrics, etc. are stored in the tracking database.
    mlflow.set_registry_uri(uri)                                 # registered models are stored in the registry database. It is for official deployment.
    mlflow.set_experiment(experiment_name)                       # project name in MLflow UI
    return mlflow
