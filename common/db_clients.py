import time
import logging
from pymongo import MongoClient
from pymongo.database import Database
from opensearchpy import OpenSearch, exceptions as os_exceptions
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biforge.common")


def get_mongo_client() -> MongoClient:
    """Returns a connected MongoDB client instance."""
    return MongoClient(settings.mongo_uri)


def get_mongo_db() -> Database:
    """Returns default 'biforge_db' database connection."""
    client = get_mongo_client()
    return client["biforge_db"]


def get_opensearch_client() -> OpenSearch:
    """Returns an OpenSearch client instance."""
    return OpenSearch(
        hosts=[settings.opensearch_url],
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False
    )


def ensure_opensearch_index(index_name: str = "biforge-ocsf-logs") -> None:
    """
    Ensures that the primary OCSF log index exists in OpenSearch with appropriate dynamic mappings.
    Retries connectivity on startup if OpenSearch is still initializing.
    """
    client = get_opensearch_client()
    index_body = {
        "mappings": {
            "properties": {
                "trace_id": {"type": "keyword"},
                "class_uid": {"type": "integer"},
                "category_uid": {"type": "integer"},
                "activity_name": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "raw_payload": {"type": "text"},
                "raw_template": {"type": "keyword"},
                "parser_confidence": {"type": "keyword"},
                "metadata.cluster_id": {"type": "keyword"},
                "metadata.parser_tier": {"type": "keyword"},
                "src_endpoint.ip": {"type": "ip"},
                "src_endpoint.port": {"type": "integer"},
                "dst_endpoint.ip": {"type": "ip"},
                "dst_endpoint.port": {"type": "integer"}
            }
        }
    }

    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            if not client.indices.exists(index=index_name):
                client.indices.create(index=index_name, body=index_body)
                logger.info(f"Created OpenSearch index '{index_name}'.")
            else:
                logger.info(f"OpenSearch index '{index_name}' already exists.")
            return
        except os_exceptions.ConnectionError:
            logger.warning(f"OpenSearch connection attempt {attempt}/{max_retries} failed. Retrying in 3 seconds...")
            time.sleep(3)
    
    raise RuntimeError("Could not establish connection to OpenSearch after max retries.")
