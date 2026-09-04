import time
import requests

URL = "http://127.0.0.1:8000/ingest"
FIXTURES = [
    "tests/fixtures/json_suricata.log",
    "tests/fixtures/cisco_asa.log",
    "tests/fixtures/syslog_ssh.log"
]

for fixture in FIXTURES:
    print(f"\nSending logs from {fixture}...")
    with open(fixture, "r") as f:
        for line in f:
            if line.strip():
                try:
                    resp = requests.post(URL, data=line.encode('utf-8'))
                    print(f"  -> [{resp.status_code}] {line.strip()[:60]}...")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  -> Failed: {e}")