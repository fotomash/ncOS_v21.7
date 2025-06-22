# zanlink/core/fetch_macro.py

"""
Fetches macroeconomic context from external sources or local mock.
Overwrites zanlink/state/macro_snapshot.json every 15 minutes.
"""

import json
from datetime import datetime
from pathlib import Path

# Simulated scrape or API call
def fetch_macro_snapshot():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "headline": "Gold rallies on Fed policy uncertainty amid soft CPI print",
        "bias": "bullish",
        "flags": ["gold", "usd", "inflation", "fomc"],
        "usd_index": 104.7,
        "fed_funds_rate": 5.25,
        "oil": 78.2,
        "relevant_to": ["XAUUSD", "USDJPY", "GOLD"]
    }

if __name__ == "__main__":
    macro = fetch_macro_snapshot()
    path = Path("zanlink/state/macro_snapshot.json")
    path.write_text(json.dumps(macro, indent=2))
    print(f"[✓] Macro snapshot updated: {macro['timestamp']}")
