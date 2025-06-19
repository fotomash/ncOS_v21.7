from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from agents.smc_router import SMCRouter as BaseSMCRouter
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitOpenError


class SMCRouter(BaseSMCRouter):
    """SMCRouter with simple circuit breaker protection for handlers."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._handlers: Dict[str, Any] = {}
        self._breakers: Dict[str, CircuitBreaker] = {}
        self.metrics = {"router_metrics": {"circuit_breaker_rejections": 0}}

    def register_handler(self, strategy_id: str, handler_id: str, handler: Any) -> None:
        cb_config = CircuitBreakerConfig(failure_threshold=3, success_threshold=1, timeout=timedelta(seconds=1))
        self._handlers[strategy_id] = handler
        self._breakers[strategy_id] = CircuitBreaker(f"{strategy_id}.{handler_id}", cb_config)

    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        strategy_id = request["strategy_id"]
        handler = self._handlers[strategy_id]
        breaker = self._breakers[strategy_id]
        try:
            return await breaker.call(handler.process, request)
        except CircuitOpenError:
            self.metrics["router_metrics"]["circuit_breaker_rejections"] += 1
            return {"status": "degraded"}
        except Exception as exc:  # pragma: no cover - simple stub
            return {"error": str(exc)}

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
