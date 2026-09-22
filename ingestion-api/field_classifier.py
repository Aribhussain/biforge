import re
import yaml
import os

class FieldClassifier:
    def __init__(self, config_filename="sources.yaml"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, config_filename)
        
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        
    def classify(self, log_message, source_port):
        category = "unknown"
        for source in self.config.get("sources", []):
            if source.get("port") == source_port:
                category = source.get("ocsf_class")
                break
                
        ips = self.ip_pattern.findall(log_message)
        return {
            "class_name": category,
            "src_ip": ips[0] if len(ips) > 0 else None,
            "dest_ip": ips[1] if len(ips) > 1 else None
        }

if __name__ == "__main__":
    classifier = FieldClassifier()
    
    # Simulated raw Fortinet firewall log
    sample_log = "Oct 12 04:32:11 192.168.1.100 fortigate: date=2026-09-22 time=10:13:00 devname=FW1 devid=FGT40 srcip=10.0.0.5 dstip=172.16.0.8 action=accept"
    
    # Test the classification against port 5140 (Fortinet)
    result = classifier.classify(sample_log, 5140)
    print(f"Classification Result: {result}")