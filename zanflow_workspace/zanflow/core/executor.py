"""
executor.py
Main orchestration of modules to decide and execute a trade.
"""
from typing import Dict, Any
from .context_analyzer import analyze_context
from .liquidity_engine import detect_sweeps
from .structure_validator import confirm_structure_shift
from .entry_trigger import identify_fvg_entry
from .risk_manager import compute_risk
from .journal import log_trade

def execute_trade(agent_config: Dict[str, Any]) -> Dict[str, Any]:
    context = analyze_context(agent_config)
    if not context.get("bias"):
        return {"status": "no_bias"}

    sweep_data = detect_sweeps(agent_config, context)
    if not sweep_data.get("inducement"):
        return {"status": "no_sweep"}

    structure = confirm_structure_shift(sweep_data, context)
    if not structure.get("confirmed"):
        return {"status": "structure_invalid"}

    entry_zone = identify_fvg_entry(structure, agent_config)
    if not entry_zone:
        return {"status": "no_fvg"}

    risk = compute_risk(entry_zone, structure, agent_config)
    if risk.get("rr", 0) < agent_config.get("min_rr", 2.0):
        log_trade(agent_config, context, sweep_data, structure, entry_zone, risk, success=False, reason="RR too low")
        return {"status": "rr_filter"}

    log_trade(agent_config, context, sweep_data, structure, entry_zone, risk, success=True)
    return {
        "status": "executed",
        "entry": entry_zone["entry_price"],
        "sl": risk["stop_loss"],
        "tp": risk["take_profit"]
    }
