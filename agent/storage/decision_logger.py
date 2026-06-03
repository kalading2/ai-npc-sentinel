import json
from datetime import datetime
import os

LOG_DIR = "data/decision_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_decision(session_id: str, state: dict, output: dict):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "input_state": state,
        "output": output
    }
    file_path = os.path.join(LOG_DIR, f"{session_id}.jsonl")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")