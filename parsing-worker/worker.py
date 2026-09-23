import json
import logging
from kafka import KafkaConsumer
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from common.config import settings
from common.db_clients import get_mongo_db, ensure_opensearch_index, get_opensearch_client
from .tier0_parsers import parse_tier0
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biforge.parsing")

# Initialize Tier 1 Drain3 Engine
config = TemplateMinerConfig()
config.load("parsing-worker/drain3_config.ini")
template_miner = TemplateMiner(config=config)

def process_stream():
    logger.info("Starting BiForge Parsing Worker...")
    ensure_opensearch_index()
    db = get_mongo_db()
    os_client = get_opensearch_client()
    
    consumer = KafkaConsumer(
        'raw-events',
        bootstrap_servers=[settings.queue_broker],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        api_version=(2, 5, 0)
    )
    
    for message in consumer:
        payload = message.value
        raw_data = payload.get("raw_payload", "")
        
        if not raw_data:
            continue

        # 1. Verbatim Storage (Ground truth for Tier 2 auditing)
        db.raw_logs.insert_one(payload)
        
        # 2. Hot-Path Parsing (Tier 1)
        parsed_data, confidence = parse_tier0(raw_data)
        template = "N/A"
        
        if confidence == "low":
            # Determine if it's slightly mutated (Medium) or completely anomalous (Flagged/Tier 3)
            syslog_months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
            
            if not raw_data.startswith(syslog_months) or "CRITICAL_ANOMALY" in raw_data:
                # Highly ambiguous: Fails syslog standards, route to Tier 3
                confidence = "flagged"
                template = "REQUIRES_AI_EXTRACTION"
                parsed_data = {"error": "schema_mismatch_routed_to_tier3"}
            else:
                # Mutated format: Process through Drain3 (Tier 2)
                result = template_miner.add_log_message(raw_data)
                template = result["template_mined"]
                parsed_data = {"drain3_cluster_id": result["cluster_id"]}
                confidence = "medium"
                
        # 3. OCSF Normalization & Indexing
        ocsf_doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "class_uid": 4001,
            "category_uid": 4,
            "activity_name": "Network Traffic",
            "raw_payload": raw_data,
            "raw_template": template,
            "parser_confidence": confidence,
            "extracted": parsed_data
        }
        
        os_client.index(index="biforge-ocsf-logs", body=ocsf_doc)
        logger.info(f"Indexed log with confidence: {confidence}")

if __name__ == "__main__":
    process_stream()