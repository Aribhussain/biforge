import logging
import requests
import json
from datetime import datetime, timezone
from kafka import KafkaConsumer
from common.db_clients import get_opensearch_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biforge.tiebreaker")

def evaluate_edge_case(raw_payload: str) -> str:
    """Queries local offline Ollama (Qwen2.5-Coder) to resolve ambiguous logs."""
    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "qwen2.5-coder:3b",
                "prompt": f"You are a SIEM parser. Extract key entities (IP, Port, Protocol, Action) from this raw log and return it as JSON:\n{raw_payload}",
                "stream": False,
                "format": "json"
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "{}")
    except Exception as e:
        logger.error(f"Offline LLM inference failed: {e}")
    return "{}"

def run_tiebreaker_loop():
    logger.info("Starting Tier 3 Offline LLM Tiebreaker...")
    
    # Connect to the Redpanda queue and OpenSearch
    consumer = KafkaConsumer(
        'ambiguous-logs',
        bootstrap_servers=['redpanda:9092'],
        auto_offset_reset='earliest',
        group_id='tiebreaker-group-v2',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    os_client = get_opensearch_client()

    for message in consumer:
        log_data = message.value
        raw_payload = log_data.get("raw_payload", "")
        logger.info(f"Picked up ambiguous log from queue: {raw_payload}")
        
        # 1. Ask Qwen to parse the messy string
        llm_json_str = evaluate_edge_case(raw_payload)
        
        try:
            extracted_data = json.loads(llm_json_str)
        except json.JSONDecodeError:
            extracted_data = {"error": "LLM JSON parsing failed", "raw": llm_json_str}

        # 2. Package into OCSF format with 'High' confidence
        ocsf_doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "class_uid": 4001,
            "category_uid": 4,
            "activity_name": "Network Traffic",
            "raw_payload": raw_payload,
            "parser_confidence": "high (Tier 3 LLM)",
            "extracted": extracted_data
        }

        # 3. Index directly to OpenSearch
        try:
            os_client.index(index="biforge-ocsf-logs", body=ocsf_doc)
            logger.info("Successfully indexed LLM-parsed log to OpenSearch.")
        except Exception as e:
            logger.error(f"OpenSearch indexing failed: {e}")

if __name__ == "__main__":
    run_tiebreaker_loop()