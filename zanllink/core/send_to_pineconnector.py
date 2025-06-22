# zanlink/core/send_to_pineconnector.py

"""
Send the latest high-confidence signal to PineConnector webhook.
Supports real-time strategy visualization in TradingView.
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# Example: https://pineconnector.net/docs/#webhooks
WEBHOOK_URL = "https://webhook.pineconnector.net/YOUR_TOKEN"
SIGNAL_FILE = Path("zanlink/state/smc_events_30T.json")
LOG_FILE = Path("zanlink/logs/pine_sent_log.jsonl")

CONFIDENCE_THRESHOLD = 0.8

def extract_latest_signal():
    data = json.loads(SIGNAL_FILE.read_text())
    high_conf = [s for s in data if s.get("signal_score", 0) >= CONFIDENCE_THRESHOLD]
    sorted_data = sorted(high_conf, key=lambda s: s['timestamp'], reverse=True)
    return sorted_data[0] if sorted_data else None

def send_signal_to_pine():
    signal = extract_latest_signal()
    if not signal:
        print("[!] No qualifying signal found.")
        return

    payload = {
        "ticker": signal["pair"],
        "action": signal["strategy"],
        "price": signal.get("price"),
        "notes": signal.get("notes") or ""
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[→] Sent to PineConnector: {payload}")
    print(f"[✓] Status: {response.status_code}")

    # Log the send
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "signal": signal,
        "status_code": response.status_code
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    send_signal_to_pine()
