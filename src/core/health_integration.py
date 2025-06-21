"""
Health Check Integration for NCOS Agents
Integrates monitoring into existing agents
"""

import time
from typing import Dict, Any

from monitoring import health_monitor
from production_logging import get_logger

logger = get_logger(__name__)


class MonitoredAgent:
    """Base class for monitored agents"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = get_logger(f"agent.{agent_id}", agent_id=agent_id)

        # Register health check
        health_monitor.register_health_check(
            f"agent_{agent_id}",
            self.health_check
        )

    async def health_check(self) -> Dict[str, Any]:
        """Agent health check implementation"""
        return {
            "agent_id": self.agent_id,
            "status": "healthy",
            "last_execution": getattr(self, "last_execution", None)
        }

    async def execute_with_monitoring(self, func, *args, **kwargs):
        """Execute function with monitoring"""
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # Record success metrics
            execution_time = time.time() - start_time
            await health_monitor.record_agent_metric(
                self.agent_id,
                "execution_time",
                execution_time
            )
            await health_monitor.record_agent_metric(
                self.agent_id,
                "success_count",
                1
            )

            self.last_execution = time.time()
            return result

        except Exception as e:
            # Record failure metrics
            await health_monitor.record_agent_metric(
                self.agent_id,
                "error_count",
                1
            )

            self.logger.error(f"Agent execution failed", exc_info=True)
            raise
