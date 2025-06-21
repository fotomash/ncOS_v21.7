"""
context_analyzer.py
Analyzes higher timeframe chart to determine Wyckoff phase and directional bias.
"""
from typing import Dict, Any, List
import pandas as pd

def analyze_context(agent_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze higher timeframe context to extract:
      - bias: "bullish", "bearish", or None
      - wyckoff_phase: str
      - poi_levels: List[float]
    """
    # TODO: load HTF price data, e.g., via agent_config['data_source']
    raise NotImplementedError
