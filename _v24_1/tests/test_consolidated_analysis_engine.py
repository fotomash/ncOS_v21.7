import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import asyncio
import pandas as pd
from unittest.mock import AsyncMock
from _v24_1.ncos_v24_1_consolidated_analysis_engine import ConsolidatedAnalysisEngine


def _mock_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=20, freq='1H')
    df = pd.DataFrame({
        'Open': 1.0,
        'High': 1.0,
        'Low': 1.0,
        'Close': 1.0,
        'Volume': 100
    }, index=dates)
    return {'h1': df}


def test_analyze_comprehensive_success():
    engine = ConsolidatedAnalysisEngine()
    data = _mock_data()
    result = asyncio.run(engine.analyze_comprehensive('EURUSD', data, 'h1'))
    assert result['symbol'] == 'EURUSD'
    assert 'overall_assessment' in result


def test_analyze_comprehensive_with_failure():
    engine = ConsolidatedAnalysisEngine()
    data = _mock_data()
    engine.structure_analyzer.analyze = AsyncMock(side_effect=Exception('fail'))
    result = asyncio.run(engine.analyze_comprehensive('EURUSD', data, 'h1'))
    assert result['status'] == 'error'
    assert 'fail' in result['error']
