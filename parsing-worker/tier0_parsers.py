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
    
    # 2. Strict Match for Clean Synthetic Logs (Tier 1 Fast Path)
    clean_fw_pattern = r'^[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+(?P<host_ip>\S+)\s+fortigate:\s+devname=(?P<devname>\S+)\s+srcip=(?P<srcip>\S+)\s+dstip=(?P<dstip>\S+)\s+action=(?P<action>accept|drop|deny)$'
    fortigate_match = re.match(clean_fw_pattern, raw_log, re.IGNORECASE)
    if fortigate_match:
        return fortigate_match.groupdict(), "high"
    
    # 3. RFC3164 Syslog (Cisco ASA, standard Linux)
    syslog_match = re.match(r'^<(\d+)>(.*)', raw_log)
    if syslog_match:
        return {"syslog_pri": syslog_match.group(1), "message": syslog_match.group(2)}, "medium"
        
    return None, "low"