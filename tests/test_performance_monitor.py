import types
import asyncio
import sys

sys.modules.setdefault("yaml", types.ModuleType("yaml"))

from agents.performance_monitor import PerformanceMonitor

class DummyOrch:
    def __init__(self):
        self.vector_engine = types.SimpleNamespace(get_vector_store_stats=lambda: {"total_vectors": 1})
        self.agents = {"a": types.SimpleNamespace(get_status=lambda: {"status": "ok"})}

class DummyState:
    memory_usage_mb = 0.0
    processed_files = []
    active_agents = []
    trading_signals = []

async def run(coro):
    return await coro

def test_collect_report():
    monitor = PerformanceMonitor(DummyOrch(), DummyState(), interval=0)
    report = asyncio.run(monitor.collect_report())
    assert "memory" in report
    assert "vector_store" in report
    assert report["agents"]["a"]["status"] == "ok"
