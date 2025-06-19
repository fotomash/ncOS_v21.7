import asyncio

from agents.liquidity_sniper import LiquiditySniperAgent
from agents.entry_executor_smc import EntryExecutorSMCAgent


class DummyOrchestrator:
    def __init__(self):
        self.calls = []

    async def route_trigger(self, name, payload, state):
        self.calls.append((name, payload, state))


def test_liquidity_sniper_trigger():
    orch = DummyOrchestrator()
    agent = LiquiditySniperAgent(orch, {})
    asyncio.run(agent.handle_trigger("liquidity_pool_identified", {"level": 1}, {}))
    assert orch.calls == [("liquidity_sniper.pool_identified", {"level": 1}, {})]


def test_entry_executor_trigger():
    orch = DummyOrchestrator()
    agent = EntryExecutorSMCAgent(orch, {})
    asyncio.run(agent.handle_trigger("precision_entry", {"symbol": "TEST"}, {}))
    assert orch.calls == [("execution.entry.submitted", {"symbol": "TEST"}, {})]
