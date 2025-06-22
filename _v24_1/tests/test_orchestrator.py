
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initializes correctly"""
    from core.orchestrators.enhanced_core_orchestrator import EnhancedCoreOrchestrator

    config = {"engines": {"market_structure": {"enabled": True}}}
    orch = EnhancedCoreOrchestrator(config)

    assert orch is not None
    assert orch.active_signals == []
