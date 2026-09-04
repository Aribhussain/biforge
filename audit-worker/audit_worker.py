import time
import logging
from common.db_clients import get_mongo_db, get_opensearch_client
from .piplup_engine import run_piplup_reconciliation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biforge.audit")

def run_audit_loop():
    logger.info("Starting BiForge Async Audit Worker...")
    db = get_mongo_db()
    os_client = get_opensearch_client()
    
    while True:
        logger.info("Executing Tier 2 PIPLUP reconciliation cycle...")
        result = run_piplup_reconciliation()
        logger.info(f"Reconciliation complete: {result}")
        # Run every 60 seconds for Phase 1 testing
        time.sleep(60)

if __name__ == "__main__":
    run_audit_loop()