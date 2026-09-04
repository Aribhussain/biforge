FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY parsing-worker/ ./parsing-worker/

CMD ["python", "-m", "parsing-worker.worker"]