import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Centralized configuration management loaded from environment variables or defaults.
    """
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://tf_admin:biforge_pass_2026@mongodb:27017/?authSource=admin")
    opensearch_url: str = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
    queue_broker: str = os.getenv("QUEUE_BROKER", "redpanda:9092")
    queue_topic: str = os.getenv("QUEUE_TOPIC", "raw-logs")
    fastapi_port: int = int(os.getenv("FASTAPI_PORT", "8000"))
    pythonunbuffered: int = int(os.getenv("PYTHONUNBUFFERED", "1"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
