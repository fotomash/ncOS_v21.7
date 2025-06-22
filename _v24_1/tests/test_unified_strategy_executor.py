import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import asyncio
import pandas as pd
from _v24_1.ncos_v24_1_unified_strategy_executor import UnifiedStrategyExecutor


def _mock_market_df():
    return pd.DataFrame({
        'Open': [1.0, 1.0],
        'High': [1.0, 1.0],
        'Low': [1.0, 1.0],
        'Close': [1.0, 1.0],
        'Volume': [100, 100]
    })


def _base_analysis():
    return {
        'analysis': {
            'structure': {'htf_bias': 'Bullish', 'choch_detected': True, 'bos_detected': True, 'confidence': 0.8},
            'liquidity': {'sweep_probability': 0.7},
            'smc': {'fvg_zones': [{'high':1.0, 'low':1.0, 'type':'bullish'}]},
            'confluence': {'overall_confluence': 0.8, 'rsi_confluence': 0.8}
        },
        'confluence_score': 0.8
    }


def test_execute_strategy_inv_success():
    executor = UnifiedStrategyExecutor({'risk_config': {'account_size': 10000}})
    market_data = {'m15': _mock_market_df()}
    analysis_result = _base_analysis()
    result = asyncio.run(executor.execute_strategy('Inv', market_data, analysis_result, 'EURUSD'))
    assert result['status'] == 'ready'
    assert result['strategy'] == 'Inv'


def test_execute_strategy_missing_price_data():
    executor = UnifiedStrategyExecutor({'risk_config': {'account_size': 10000}})
    executor._get_latest_price_data = lambda data: None
    market_data = {'m15': _mock_market_df()}
    analysis_result = _base_analysis()
    result = asyncio.run(executor.execute_strategy('Inv', market_data, analysis_result, 'EURUSD'))
    assert result['status'] == 'error'

