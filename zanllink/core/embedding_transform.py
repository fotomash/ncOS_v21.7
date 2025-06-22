# zanlink/core/embedding.py

"""
Transforms SMC signal events into vectorizable text for use in vector DBs (e.g. Chroma, FAISS).

This enables long-term memory, similarity search, and contextual recall.

Each signal is reduced to a semantically meaningful string.
"""

from typing import Dict

def smc_event_to_text(signal: Dict) -> str:
    """
    Convert a structured SMC event JSON object into a natural language text summary.
    Used for embedding and similarity search.
    """
    ts = signal.get("timestamp", "unknown time")
    tf = signal.get("timeframe", "unknown TF")
    evt = signal.get("event_type", "event")
    val = signal.get("indicator_value")
    px = signal.get("price")
    structure = signal.get("structure_context")
    notes = signal.get("notes") or ""

    summary = f"At {ts} on the {tf} chart, a {evt} signal was detected."
    if val is not None:
        summary += f" Indicator value was {val}."
    if px:
        summary += f" Price was around {px}."
    if structure:
        summary += f" Structure context was {structure}."
    if notes:
        summary += f" Notes: {notes}."

    return summary.strip()
