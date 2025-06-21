"""Helper functions providing GPT instructions and auto-progression config."""

from __future__ import annotations

from typing import Any, Dict

_DEF_AGENT_INSTRUCTIONS = {
    "default": "Use available agents to process user commands with context-aware logic."
}


def get_agent_instructions(agent: str | None = None) -> str:
    """Return instructions for the given agent."""
    if not agent:
        agent = "default"
    return _DEF_AGENT_INSTRUCTIONS.get(agent, _DEF_AGENT_INSTRUCTIONS["default"])


# Default auto-progression configuration used by the EnhancedLLMCLI

_DEF_AUTO_PROGRESSION = {
    "triggers": {
        "pattern_confidence_threshold": 0.8,
        "risk_score_threshold": 0.7,
        "consensus_threshold": 0.9,
        "session_save_interval": 300,
    },
    "actions": {
        "high_confidence_pattern": "generate_signal",
        "high_risk": "halt_trading",
        "consensus_reached": "execute_recommendation",
        "session_save": "save_session_and_escalate",
        "timeout": "request_human_review",
    },
}


def get_auto_progression_config() -> Dict[str, Any]:
    """Return the auto-progression configuration."""
    return _DEF_AUTO_PROGRESSION.copy()


__all__ = ["get_agent_instructions", "get_auto_progression_config"]
