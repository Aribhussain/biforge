import json
from kafka import KafkaProducer

print("Connecting to Redpanda inside Docker network...")
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

test_log = {
    "raw_payload": "May 10 08:14:02 rogue-device ERR: [SysAuth] Failed login root from 172.16.0.42 port 44321 via SSH"
}

producer.send('ambiguous-logs', test_log)
producer.flush()
print("Successfully sent test edge-case log to Redpanda!")