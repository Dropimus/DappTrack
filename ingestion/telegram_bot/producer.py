import json
from datetime import datetime

def send_to_queue(data):
    filename = f"queue_{datetime.now().date()}.jsonl"
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")
