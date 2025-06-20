"""Enhanced Menu System for ncOS v21.7

This module provides a lightweight menu generator similar to the
v8.1 `EnhancedMenuSystem`. It generates categorized menu options and
includes current agent status information from the orchestrator.
"""
from __future__ import annotations

from typing import Any, Dict
import yaml


class EnhancedMenuSystem:
    """Generate a structured menu with agent status information."""

    def __init__(self, orchestrator: Any) -> None:
        self.orchestrator = orchestrator

    def generate_menu(self) -> Dict[str, Any]:
        """Return menu dict with categories and agent status."""
        if hasattr(self.orchestrator, "generate_enhanced_menu"):
            menu = self.orchestrator.generate_enhanced_menu()
        else:
            menu = {"title": "ncOS Menu", "categories": {}}

        agent_status: Dict[str, str] = {}
        agents = getattr(self.orchestrator, "agents", {})
        for agent_id, agent_info in agents.items():
            if isinstance(agent_info, dict):
                agent_status[agent_id] = agent_info.get("status", "unknown")
            elif hasattr(agent_info, "get_status"):
                try:
                    agent_status[agent_id] = agent_info.get_status().get("status", "unknown")
                except Exception:
                    agent_status[agent_id] = "unknown"
            else:
                agent_status[agent_id] = "unknown"

        menu["agent_status"] = agent_status
        return menu

    def format_menu(self, menu: Dict[str, Any]) -> str:
        """Return YAML-formatted menu."""
        return yaml.dump(menu, sort_keys=False)


__all__ = ["EnhancedMenuSystem"]
