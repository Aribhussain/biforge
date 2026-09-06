FROM python:3.11-slim

WORKDIR /app

# Copy the global requirements file from the root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared core and the ingestion API code
COPY common/ ./common/
COPY ingestion-api/ ./ingestion-api/

EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "ingestion-api.main:app", "--host", "0.0.0.0", "--port", "8000"]/3 s .