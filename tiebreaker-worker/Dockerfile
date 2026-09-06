FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY tiebreaker-worker/ ./tiebreaker-worker/

CMD ["python", "-m", "tiebreaker-worker.llm_worker"]