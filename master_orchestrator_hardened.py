from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from agents.master_orchestrator import MasterOrchestrator as BaseMasterOrchestrator
from circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
)


class MasterOrchestrator(BaseMasterOrchestrator):
    """Master orchestrator with basic circuit breaker logic."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._agents: Dict[str, Any] = {}
        self._workflows: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, agent: Any) -> None:
        cb_config = CircuitBreakerConfig(failure_threshold=3, success_threshold=1, timeout=timedelta(seconds=1))
        self._agents[agent_id] = agent
        self._breakers[agent_id] = CircuitBreaker(agent_id, cb_config)

    def register_workflow(self, workflow_id: str, workflow: Dict[str, Any]) -> None:
        self._workflows[workflow_id] = workflow

    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        workflow = self._workflows[workflow_id]
        results: Dict[str, Any] = {}
        failed_agents = []
        status = "success"

        for step in workflow["steps"]:
            agent_id = step["agent_id"]
            critical = step.get("critical", True)
            agent = self._agents[agent_id]
            breaker = self._breakers[agent_id]
            try:
                results[agent_id] = await breaker.call(agent.execute, {}, context)
            except CircuitOpenError:
                results[agent_id] = {"reason": "circuit_open"}
                failed_agents.append(agent_id)
                status = "degraded"
            except Exception as exc:
                results[agent_id] = {"error": str(exc)}
                failed_agents.append(agent_id)
                status = "degraded"
                if critical:
                    break

        return {"status": status, "results": results, "failed_agents": failed_agents}

    def get_health_status(self) -> Dict[str, Any]:
        open_circuits = sum(1 for b in self._breakers.values() if b.state == CircuitState.OPEN)
        return {"open_circuits": open_circuits}
