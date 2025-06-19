"""Utility helpers for CLI configuration."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Dict


def _load_yaml(path: Path) -> Dict[str, Any]:
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_agent_instructions() -> Dict[str, Any]:
    """Return agent instructions from YAML if available."""
    path = Path(__file__).with_name("agent_instructions.yaml")
    return _load_yaml(path)


def get_auto_progression_config() -> Dict[str, Any]:
    """Return auto-progression configuration."""
    path = Path(__file__).with_name("auto_progression.yaml")
    config = _load_yaml(path)
    if config:
        return config

    return {
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
            "timeout": "save_session_and_escalate",
            "session_save": "save_session_and_escalate",
            "agent_disagreement": "request_human_review",
        },
    }
