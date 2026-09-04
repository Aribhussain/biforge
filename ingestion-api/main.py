import json
import logging
import time
from fastapi import FastAPI, Request, HTTPException
from kafka import KafkaProducer
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biforge.ingestion")

app = FastAPI(title="BiForge Ingestion Gateway")

# Initialize synchronous Kafka Producer using kafka-python-ng
try:
    producer = KafkaProducer(
        bootstrap_servers=[settings.queue_broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(2, 5, 0)
    )
    logger.info(f"Connected to Redpanda broker at {settings.queue_broker}")
except Exception as e:
    logger.error(f"Failed to connect to broker: {e}")
    producer = None

@app.post("/ingest")
async def ingest_log(request: Request):
    if not producer:
        raise HTTPException(status_code=503, detail="Message broker unavailable")
    
    try:
        # Attempt to parse as JSON first (for Suricata/CloudTrail)
        payload = await request.json()
    except Exception:
        # Fallback for raw Syslog or plain text (Cisco ASA, pfSense)
        raw_body = await request.body()
        payload = {"raw_data": raw_body.decode("utf-8", errors="replace")}
        
    try:
        payload["biforge_ingest_time"] = time.time()
        producer.send(settings.queue_topic, value=payload)
        producer.flush()
        return {"status": "success", "message": "Log ingested successfully"}
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enqueue log")

@app.get("/health")
def health_check():
    return {"status": "healthy", "broker_connected": producer is not None}