import json
import re
from typing import Tuple, Optional, Dict, Any

def parse_tier0(raw_log: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Attempts fast, deterministic parsing before falling back to Drain3."""
    # 1. JSON (Suricata, CloudTrail)
    try:
        data = json.loads(raw_log)
        return data, "high"
    except json.JSONDecodeError:
        pass
    
    # 2. RFC3164 Syslog (Cisco ASA, standard Linux)
    syslog_match = re.match(r'^<(\d+)>(.*)', raw_log)
    if syslog_match:
        return {"syslog_pri": syslog_match.group(1), "message": syslog_match.group(2)}, "medium"
        
    return None, "low"