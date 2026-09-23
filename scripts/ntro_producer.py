import json
import time
import random
from kafka import KafkaProducer

# Initialize Redpanda Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:19092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def stream_synthetic_logs(num_logs=1000, topic='raw-events'):
    print(f"Generating and streaming {num_logs} synthetic NTRO-grade logs to '{topic}'...")
    
    # Templates designed to stress-test the 3-tier pipeline
    templates = [
        # Tier 1 Target: Clean, predictable firewall log
        "Oct 12 04:32:11 {ip1} fortigate: devname=FW1 srcip={ip1} dstip={ip2} action=accept",
        
        # Tier 2 Target: Format drift, unexpected fields for PIPLUP to reconcile
        "Oct 12 04:32:15 {ip1} fortigate: devname=FW1 [NET_WARN] source={ip1} destination={ip2} action=DROP reason=policy_violation_auth_fail",
        
        # Tier 3 Target: Highly ambiguous, missing standard headers, requires AI extraction
        "CRITICAL_ANOMALY_DETECTED [node_88] hex_payload_drop tgt_addr:{ip2} orig_addr:{ip1} :: unauthorized access attempt blocked"
    ]
    
    count = 0
    for _ in range(num_logs):
        # Generate random subnets
        ip1 = f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}"
        ip2 = f"172.16.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        # Select a random template and inject the IPs
        raw_log = random.choice(templates).replace("{ip1}", ip1).replace("{ip2}", ip2)
        
        payload = {"raw_payload": raw_log}
        producer.send(topic, payload)
        count += 1
        
        # 5 millisecond delay to simulate rapid network streaming
        time.sleep(0.005) 
            
    producer.flush()
    print(f"Streaming complete. Published {count} synthetic logs to Redpanda.")

if __name__ == "__main__":
    stream_synthetic_logs(1500)