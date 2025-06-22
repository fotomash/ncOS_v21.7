import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import asyncio
import pandas as pd
from unittest.mock import AsyncMock
from _v24_1.core.orchestrators.ncos_v24_1_main_orchestrator import NCOSMainOrchestrator


def test_orchestrator_loads_default_configs(tmp_path):
    orch = NCOSMainOrchestrator(config_dir=tmp_path)
    system_cfg = orch.config.get('system_config')
    assert system_cfg['system']['version'] == '24.1.0'


async def run(coro):
    return await coro


def test_analyze_symbol_returns_error_on_fetch_failure(tmp_path):
    orch = NCOSMainOrchestrator(config_dir=tmp_path)
    orch.data_pipeline.fetch_and_process = AsyncMock(return_value={'status': 'error', 'message': 'fail'})
    result = asyncio.run(orch.analyze_symbol('EURUSD'))
    assert result['status'] == 'error'
    assert result['message'] == 'fail'


def test_analyze_symbol_returns_error_on_analysis_failure(tmp_path):
    orch = NCOSMainOrchestrator(config_dir=tmp_path)
    orch.data_pipeline.fetch_and_process = AsyncMock(return_value={'status': 'success', 'data': {'m15': pd.DataFrame()}})
    orch.analysis_engine.run_full_analysis = AsyncMock(return_value={'status': 'error', 'message': 'analysis failed'})
    result = asyncio.run(orch.analyze_symbol('EURUSD'))
    assert result['status'] == 'error'
    assert result['message'] == 'analysis failed'
