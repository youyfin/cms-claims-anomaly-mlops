.PHONY: setup demo real run test lint mlflow-ui clean

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements-dev.txt && pip install -e .

demo:
	python scripts/generate_demo_data.py --rows 12000
	python scripts/run_pipeline.py

real:
	python scripts/download_cms_data.py
	python scripts/run_pipeline.py

run:
	python scripts/run_pipeline.py

test:
	pytest -q

lint:
	ruff check src scripts tests

mlflow-ui:
	mlflow ui --backend-store-uri sqlite:///artifacts/mlflow/mlflow.db --port 5000

clean:
	rm -rf data/processed/* artifacts/*
