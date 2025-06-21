"""
journal.py
Logs every evaluated setup and executed trade for post-trade analysis.
"""
import json
from datetime import datetime
from typing import Dict, Any

JOURNAL_PATH = "journal_logs.jsonl"

def log_trade(agent_config: Dict[str, Any],
              context: Dict[str, Any],
              sweep_data: Dict[str, Any],
              structure: Dict[str, Any],
              entry_zone: Dict[str, Any],
              risk: Dict[str, Any],
              success: bool,
              reason: str = None) -> None:
    """
    Append a JSON line to the journal with full details.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_config.get('agent_name'),
        "context": context,
        "sweep_data": sweep_data,
        "structure": structure,
        "entry_zone": entry_zone,
        "risk": risk,
        "success": success,
        "reason": reason
    }
    with open(JOURNAL_PATH, 'a') as f:
        f.write(json.dumps(record) + "\n")
