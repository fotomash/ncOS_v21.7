"""
Production Monitoring and Health Check System
Exposes metrics and health endpoints for external monitoring
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import psutil

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Collects and aggregates system metrics"""

    def __init__(self, retention_minutes: int = 60):
        self.metrics: Dict[str, deque] = {}
        self.retention = timedelta(minutes=retention_minutes)
        self._lock = asyncio.Lock()

    async def record(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value"""
        async with self._lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = deque()

            point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {}
            )

            self.metrics[metric_name].append(point)

            # Clean old metrics
            await self._cleanup_old_metrics(metric_name)

    async def _cleanup_old_metrics(self, metric_name: str):
        """Remove metrics older than retention period"""
        cutoff = datetime.now() - self.retention

        while self.metrics[metric_name] and self.metrics[metric_name][0].timestamp < cutoff:
            self.metrics[metric_name].popleft()

    async def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        async with self._lock:
            if metric_name not in self.metrics or not self.metrics[metric_name]:
                return {"error": "No data available"}

            values = [p.value for p in self.metrics[metric_name]]

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "last": values[-1],
                "last_timestamp": self.metrics[metric_name][-1].timestamp.isoformat()
            }

class HealthMonitor:
    """System health monitoring and reporting"""

    def __init__(self):
        self.collectors = MetricsCollector()
        self.health_checks: Dict[str, Any] = {}
        self.start_time = datetime.now()

    async def collect_system_metrics(self):
        """Collect system-level metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        await self.collectors.record("system.cpu.usage", cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        await self.collectors.record("system.memory.usage", memory.percent)
        await self.collectors.record("system.memory.available", memory.available)

        # Disk usage
        disk = psutil.disk_usage('/')
        await self.collectors.record("system.disk.usage", disk.percent)

        # Process metrics
        process = psutil.Process()
        await self.collectors.record("process.cpu.percent", process.cpu_percent())
        await self.collectors.record("process.memory.rss", process.memory_info().rss)
        await self.collectors.record("process.threads", process.num_threads())

    async def record_agent_metric(self, agent_id: str, metric: str, value: float):
        """Record agent-specific metric"""
        await self.collectors.record(
            f"agent.{metric}",
            value,
            labels={"agent_id": agent_id}
        )

    async def record_workflow_metric(self, workflow_id: str, metric: str, value: float):
        """Record workflow-specific metric"""
        await self.collectors.record(
            f"workflow.{metric}",
            value,
            labels={"workflow_id": workflow_id}
        )

    def register_health_check(self, name: str, check_func: Any):
        """Register a health check function"""
        self.health_checks[name] = check_func

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        health_results = {}

        # Run all health checks
        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                health_results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "details": result
                }
            except Exception as e:
                health_results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

        # Collect system metrics
        await self.collect_system_metrics()

        # Get metric summaries
        metrics_summary = {}
        for metric_name in ["system.cpu.usage", "system.memory.usage", "process.cpu.percent"]:
            metrics_summary[metric_name] = await self.collectors.get_metric_summary(metric_name)

        # Calculate overall health
        unhealthy_checks = sum(1 for r in health_results.values() if r["status"] == "unhealthy")

        if unhealthy_checks == 0:
            overall_status = "healthy"
        elif unhealthy_checks < len(health_results) / 2:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "checks": health_results,
            "metrics": metrics_summary,
            "version": "v21.0.0"
        }

# Global health monitor instance
health_monitor = HealthMonitor()

# FastAPI health endpoints (optional, can use any web framework)
HEALTH_ENDPOINTS_TEMPLATE = """
from fastapi import FastAPI, Response
from monitoring import health_monitor
import json

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    health_status = await health_monitor.get_health_status()

    # Set appropriate HTTP status code
    if health_status["status"] == "healthy":
        status_code = 200
    elif health_status["status"] == "degraded":
        status_code = 200  # Still return 200 for degraded
    else:
        status_code = 503

    return Response(
        content=json.dumps(health_status, indent=2),
        status_code=status_code,
        media_type="application/json"
    )

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus-compatible metrics endpoint"""
    # Format metrics in Prometheus format
    metrics_text = ""

    # This is a simplified example - real implementation would be more comprehensive
    health_status = await health_monitor.get_health_status()

    for metric_name, summary in health_status["metrics"].items():
        if isinstance(summary, dict) and "last" in summary:
            metric_key = metric_name.replace(".", "_")
            metrics_text += f"# TYPE {metric_key} gauge\n"
            metrics_text += f"{metric_key} {summary['last']}\n"

    return Response(content=metrics_text, media_type="text/plain")

@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    # Check if system is ready to accept traffic
    health_status = await health_monitor.get_health_status()

    if health_status["status"] in ["healthy", "degraded"]:
        return {"ready": True}
    else:
        return Response(content={"ready": False}, status_code=503)

@app.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    # Simple check that the process is alive
    return {"alive": True}
"""
