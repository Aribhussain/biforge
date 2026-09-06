import logging
import requests
import time
from common.db_clients import get_mongo_db

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
    while True:
        # Phase 1 Stub: This will consume from an 'ambiguous-logs' Redpanda topic
        time.sleep(10)

if __name__ == "__main__":
    run_tiebreaker_loop()