from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Endpoint(BaseModel):
    """Network endpoint abstraction (source or destination)."""
    ip: Optional[str] = None
    port: Optional[int] = None
    hostname: Optional[str] = None


class Metadata(BaseModel):
    """Telemetry source and parsing metadata."""
    product_name: str = "BiForge-ULP"
    version: str = "2.0"
    cluster_id: Optional[str] = None
    parser_tier: Optional[str] = None


class OCSFNetworkActivity(BaseModel):
    """
    OCSF Class 4001: Network Activity Event Schema.
    Includes BiForge confidence classification tags for hot-path and background audit tracking.
    """
    class_uid: int = Field(default=4001, description="OCSF Class UID for Network Activity")
    category_uid: int = Field(default=4, description="OCSF Category UID for Network Activity")
    activity_name: str = Field(default="Network Traffic", description="Human-readable event activity")
    
    trace_id: str = Field(..., description="Unique event identifier attached at ingestion")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    src_endpoint: Optional[Endpoint] = None
    dst_endpoint: Optional[Endpoint] = None
    protocol: Optional[str] = None
    
    raw_payload: str = Field(..., description="Verbatim raw log event string")
    raw_template: Optional[str] = Field(None, description="Mined parameter log template pattern")
    
    parser_confidence: Literal["high", "medium", "corrected", "flagged"] = Field(
        default="medium",
        description="Confidence level assigned by deterministic, Drain3, or PIPLUP audit parsers"
    )
    
    metadata: Metadata = Field(default_factory=Metadata)
    additional_fields: Dict[str, Any] = Field(default_factory=dict)
