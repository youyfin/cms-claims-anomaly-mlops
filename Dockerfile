FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

COPY config ./config
COPY sql ./sql
COPY scripts ./scripts
COPY data ./data

CMD ["python", "scripts/run_pipeline.py"]
