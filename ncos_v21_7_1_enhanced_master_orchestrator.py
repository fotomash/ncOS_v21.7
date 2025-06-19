"""NCOSEnhancedMasterOrchestrator module"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from agents.master_orchestrator import MasterOrchestrator
from enhanced_core_orchestrator import ncOScoreEnhancedOrchestrator


class NCOSEnhancedMasterOrchestrator(ncOScoreEnhancedOrchestrator):
    """Enhanced orchestrator wrapper used in tests and launch scripts."""

    def __init__(self, config_path: Optional[str] = None, registry_path: str = "enhanced_agent_registry_complete.yaml"):
        super().__init__(config_path)
        self.core_orchestrator = MasterOrchestrator(self.config)
        self.agent_registry: Dict[str, Any] = self._load_agent_registry(registry_path)
        self.agents: Dict[str, Any] = {}
        self.smc_agent = None
        self.vector_agent = None
        self.liquidity_agent = None
        self.market_data_agent = None

    # ------------------------------------------------------------------
    # Configuration helpers
    def _load_agent_registry(self, path: str) -> Dict[str, Any]:
        """Load agent registry from YAML file."""
        if path and Path(path).exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
            return data.get("enhanced_ncos_agents", data.get("agents", {}))
        return {}

    def _load_enhanced_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Public wrapper for parent _load_config."""
        return self._load_config(config_path)

    # ------------------------------------------------------------------
    # Initialization
    async def _initialize_core_agents(self) -> None:
        """Initialize core trading agents (mock implementation)."""
        self.smc_agent = object()
        self.vector_agent = object()
        self.liquidity_agent = object()
        self.market_data_agent = object()
        self.agents = {
            "smc_agent": self.smc_agent,
            "vector_agent": self.vector_agent,
            "liquidity_agent": self.liquidity_agent,
            "market_data_agent": self.market_data_agent,
        }

    async def initialize_complete_system(self) -> None:
        """Initialize orchestrator and core agents."""
        await self.initialize()
        await self._initialize_core_agents()

    # ------------------------------------------------------------------
    # Public API wrappers
    def generate_complete_enhanced_menu(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.generate_enhanced_menu(context)

    def get_complete_system_status(self) -> Dict[str, Any]:
        status = self.get_enhanced_system_status()
        status["agents"] = list(self.agent_registry.keys())
        status["capabilities"] = self.config.get("features", {})
        return status

    def _detect_file_type(self, file_path: str) -> str:  # type: ignore[override]
        return super()._detect_file_type(file_path)

    def _calculate_enhanced_confluence(self, analysis_results: Dict[str, Any]) -> float:
        return self._calculate_overall_confluence(analysis_results)


__all__ = ["NCOSEnhancedMasterOrchestrator"]
