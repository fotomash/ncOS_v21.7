
"""
NCOS v24.1 - Unified Strategy Executor
Consolidates all strategy variants: Inv, MAZ2, TMC, Mentfx
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

logger = logging.getLogger('NCOS_v24.1.StrategyExecutor')

class UnifiedStrategyExecutor:
    """Unified executor for all NCOS strategy variants"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.risk_config = self.config.get('risk_config', {})
        self.execution_stats = {}

        # Strategy-specific configurations
        self.strategy_configs = {
            'Inv': {
                'mitigation_type': 'wick_allowed',
                'confluence_required': False,
                'min_rr': 2.0,
                'max_risk_per_trade': 1.0
            },
            'MAZ2': {
                'mitigation_type': 'fvg_retest',
                'confluence_required': True,
                'min_rr': 3.0,
                'max_risk_per_trade': 0.75,
                'no_body_engulf': True
            },
            'TMC': {
                'mitigation_type': 'bos_confirmation',
                'confluence_required': True,
                'min_rr': 3.5,
                'max_risk_per_trade': 1.5,
                'requires_bos': True
            },
            'Mentfx': {
                'mitigation_type': 'pattern_confirmation',
                'confluence_required': True,
                'min_rr': 2.5,
                'max_risk_per_trade': 1.0,
                'requires_candlestick_pattern': True,
                'dss_confirmation': True
            }
        }

    async def execute_strategy(self, strategy_name: str, market_data: Dict, analysis_result: Dict, symbol: str) -> Dict:
        """Execute specific strategy variant"""
        try:
            logger.info(f"Executing {strategy_name} strategy for {symbol}")

            # Get strategy configuration
            strategy_config = self.strategy_configs.get(strategy_name, {})

            # Pre-execution validation
            validation_result = self._validate_strategy_conditions(strategy_name, analysis_result, market_data)
            if not validation_result['valid']:
                return {
                    'status': 'rejected',
                    'reason': validation_result['reason'],
                    'strategy': strategy_name,
                    'symbol': symbol
                }

            # Calculate entry parameters
            entry_params = await self._calculate_entry_parameters(strategy_name, analysis_result, market_data, symbol)

            # Apply risk management
            risk_params = self._calculate_risk_management(entry_params, strategy_config, symbol)

            # Generate execution signals
            execution_signals = self._generate_execution_signals(entry_params, risk_params, strategy_config)

            # Create final execution result
            execution_result = {
                'status': 'ready',
                'strategy': strategy_name,
                'symbol': symbol,
                'entry_params': entry_params,
                'risk_params': risk_params,
                'execution_signals': execution_signals,
                'confidence_score': analysis_result.get('confluence_score', 0),
                'timestamp': datetime.utcnow().isoformat(),
                'validation': validation_result
            }

            # Log execution
            self._log_strategy_execution(execution_result)

            return execution_result

        except Exception as e:
            logger.error(f"Strategy execution failed for {strategy_name}: {e}")
            return {
                'status': 'error',
                'strategy': strategy_name,
                'symbol': symbol,
                'error': str(e)
            }

    def _validate_strategy_conditions(self, strategy_name: str, analysis: Dict, market_data: Dict) -> Dict:
        """Validate strategy-specific conditions before execution"""

        if strategy_name == 'Inv':
            return self._validate_inv_conditions(analysis, market_data)
        elif strategy_name == 'MAZ2':
            return self._validate_maz2_conditions(analysis, market_data)
        elif strategy_name == 'TMC':
            return self._validate_tmc_conditions(analysis, market_data)
        elif strategy_name == 'Mentfx':
            return self._validate_mentfx_conditions(analysis, market_data)
        else:
            return {'valid': False, 'reason': f'Unknown strategy: {strategy_name}'}

    def _validate_inv_conditions(self, analysis: Dict, market_data: Dict) -> Dict:
        """Validate Inversion strategy conditions"""
        analysis_data = analysis.get('analysis', {})

        # Check for basic structure
        structure = analysis_data.get('structure', {})
        if not structure.get('choch_detected') and not structure.get('bos_detected'):
            return {'valid': False, 'reason': 'No structural break detected'}

        # Check liquidity analysis
        liquidity = analysis_data.get('liquidity', {})
        if liquidity.get('sweep_probability', 0) < 0.5:
            return {'valid': False, 'reason': 'Low liquidity sweep probability'}

        return {'valid': True, 'reason': 'Inv conditions met'}

    def _validate_maz2_conditions(self, analysis: Dict, market_data: Dict) -> Dict:
        """Validate MAZ2 strategy conditions"""
        analysis_data = analysis.get('analysis', {})

        # Check for FVG zones
        smc = analysis_data.get('smc', {})
        if not smc.get('fvg_zones'):
            return {'valid': False, 'reason': 'No FVG zones detected'}

        # Check confluence requirements
        confluence = analysis_data.get('confluence', {})
        if confluence.get('overall_confluence', 0) < 0.7:
            return {'valid': False, 'reason': 'Insufficient confluence for MAZ2'}

        return {'valid': True, 'reason': 'MAZ2 conditions met'}

    def _validate_tmc_conditions(self, analysis: Dict, market_data: Dict) -> Dict:
        """Validate TMC strategy conditions"""
        analysis_data = analysis.get('analysis', {})

        # Require BOS confirmation
        structure = analysis_data.get('structure', {})
        if not structure.get('bos_detected'):
            return {'valid': False, 'reason': 'BOS confirmation required for TMC'}

        # Check confluence
        confluence = analysis_data.get('confluence', {})
        if confluence.get('overall_confluence', 0) < 0.75:
            return {'valid': False, 'reason': 'TMC requires high confluence'}

        return {'valid': True, 'reason': 'TMC conditions met'}

    def _validate_mentfx_conditions(self, analysis: Dict, market_data: Dict) -> Dict:
        """Validate Mentfx strategy conditions"""
        analysis_data = analysis.get('analysis', {})

        # Check for DSS confirmation
        confluence = analysis_data.get('confluence', {})
        if confluence.get('rsi_confluence', 0) < 0.6:
            return {'valid': False, 'reason': 'Mentfx requires RSI/DSS confluence'}

        # Check for candlestick patterns (simplified)
        structure = analysis_data.get('structure', {})
        if structure.get('confidence', 0) < 0.7:
            return {'valid': False, 'reason': 'Mentfx requires strong pattern confirmation'}

        return {'valid': True, 'reason': 'Mentfx conditions met'}

    async def _calculate_entry_parameters(self, strategy_name: str, analysis: Dict, market_data: Dict, symbol: str) -> Dict:
        """Calculate entry parameters based on strategy variant"""

        # Get latest price data
        latest_data = self._get_latest_price_data(market_data)
        if not latest_data:
            raise ValueError("No price data available for entry calculation")

        current_price = latest_data['Close']

        # Strategy-specific entry logic
        if strategy_name == 'Inv':
            entry_price, direction = self._calculate_inv_entry(analysis, latest_data, current_price)
        elif strategy_name == 'MAZ2':
            entry_price, direction = self._calculate_maz2_entry(analysis, latest_data, current_price)
        elif strategy_name == 'TMC':
            entry_price, direction = self._calculate_tmc_entry(analysis, latest_data, current_price)
        elif strategy_name == 'Mentfx':
            entry_price, direction = self._calculate_mentfx_entry(analysis, latest_data, current_price)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return {
            'entry_price': entry_price,
            'current_price': current_price,
            'direction': direction,
            'entry_method': f'{strategy_name}_calculated',
            'price_data': latest_data
        }

    def _calculate_inv_entry(self, analysis: Dict, latest_data: Dict, current_price: float) -> Tuple[float, str]:
        """Calculate Inv strategy entry"""
        # Inversion allows wick mitigation
        structure = analysis.get('analysis', {}).get('structure', {})
        bias = structure.get('htf_bias', 'Unknown')

        if bias == 'Bullish':
            # Enter on wick low or slight discount
            entry_price = current_price * 0.999  # Small discount
            direction = 'buy'
        else:
            # Enter on wick high or slight premium
            entry_price = current_price * 1.001  # Small premium
            direction = 'sell'

        return entry_price, direction

    def _calculate_maz2_entry(self, analysis: Dict, latest_data: Dict, current_price: float) -> Tuple[float, str]:
        """Calculate MAZ2 strategy entry"""
        # MAZ2 requires FVG midpoint entry
        smc = analysis.get('analysis', {}).get('smc', {})
        fvg_zones = smc.get('fvg_zones', [])

        if fvg_zones:
            # Use first FVG zone for entry
            fvg_zone = fvg_zones[0]
            entry_price = (fvg_zone.get('high', current_price) + fvg_zone.get('low', current_price)) / 2
            direction = 'buy' if fvg_zone.get('type') == 'bullish' else 'sell'
        else:
            # Fallback to current price with slight adjustment
            entry_price = current_price
            direction = 'buy'  # Default

        return entry_price, direction

    def _calculate_tmc_entry(self, analysis: Dict, latest_data: Dict, current_price: float) -> Tuple[float, str]:
        """Calculate TMC strategy entry"""
        # TMC waits for BOS confirmation then enters on pullback
        structure = analysis.get('analysis', {}).get('structure', {})
        bias = structure.get('htf_bias', 'Unknown')

        if bias == 'Bullish':
            # Enter on pullback after BOS
            entry_price = current_price * 0.9985  # Deeper pullback
            direction = 'buy'
        else:
            entry_price = current_price * 1.0015  # Deeper pullback
            direction = 'sell'

        return entry_price, direction

    def _calculate_mentfx_entry(self, analysis: Dict, latest_data: Dict, current_price: float) -> Tuple[float, str]:
        """Calculate Mentfx strategy entry"""
        # Mentfx waits for candlestick pattern confirmation
        confluence = analysis.get('analysis', {}).get('confluence', {})
        rsi_confluence = confluence.get('rsi_confluence', 0.5)

        if rsi_confluence > 0.6:
            # Strong RSI signal
            direction = 'buy' if rsi_confluence > 0.7 else 'sell'
            entry_price = current_price * (0.999 if direction == 'buy' else 1.001)
        else:
            entry_price = current_price
            direction = 'buy'  # Default

        return entry_price, direction

    def _calculate_risk_management(self, entry_params: Dict, strategy_config: Dict, symbol: str) -> Dict:
        """Calculate risk management parameters"""
        entry_price = entry_params['entry_price']
        direction = entry_params['direction']

        # Get risk configuration
        account_size = self.risk_config.get('account_size', 10000)
        risk_percent = strategy_config.get('max_risk_per_trade', 1.0)
        min_rr = strategy_config.get('min_rr', 2.0)

        # Calculate stop loss based on strategy
        sl_distance = self._calculate_stop_loss_distance(entry_price, symbol)

        if direction == 'buy':
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + (sl_distance * min_rr)
        else:
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - (sl_distance * min_rr)

        # Calculate position size
        risk_amount = account_size * (risk_percent / 100)
        position_size = risk_amount / sl_distance if sl_distance > 0 else 0

        return {
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'position_size': round(position_size, 2),
            'risk_amount': round(risk_amount, 2),
            'risk_reward_ratio': min_rr,
            'sl_distance': sl_distance
        }

    def _calculate_stop_loss_distance(self, entry_price: float, symbol: str) -> float:
        """Calculate stop loss distance based on symbol characteristics"""
        # Simple ATR-based calculation (would use actual ATR in production)
        if 'EUR' in symbol or 'GBP' in symbol:
            return entry_price * 0.005  # 0.5% for major FX pairs
        elif 'XAU' in symbol or 'GOLD' in symbol:
            return entry_price * 0.01   # 1% for gold
        else:
            return entry_price * 0.02   # 2% for other instruments

    def _generate_execution_signals(self, entry_params: Dict, risk_params: Dict, strategy_config: Dict) -> Dict:
        """Generate execution signals for trade placement"""
        return {
            'signal_type': 'limit_order',
            'entry_order': {
                'type': 'limit',
                'price': entry_params['entry_price'],
                'direction': entry_params['direction']
            },
            'stop_loss_order': {
                'type': 'stop',
                'price': risk_params['stop_loss']
            },
            'take_profit_order': {
                'type': 'limit',
                'price': risk_params['take_profit']
            },
            'position_size': risk_params['position_size'],
            'execution_method': 'mt5_direct'  # or other execution methods
        }

    def _get_latest_price_data(self, market_data: Dict) -> Optional[Dict]:
        """Get latest price data from market data"""
        for tf in ['m1', 'm5', 'm15']:
            if tf in market_data:
                df = market_data[tf]
                if not df.empty:
                    return df.iloc[-1].to_dict()
        return None

    def _log_strategy_execution(self, execution_result: Dict):
        """Log strategy execution details"""
        log_dir = Path("journal/strategy_executions")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        strategy = execution_result['strategy']
        symbol = execution_result['symbol']

        log_file = log_dir / f"{strategy}_{symbol}_{timestamp}.json"

        try:
            with open(log_file, 'w') as f:
                json.dump(execution_result, f, indent=2, default=str)
            logger.info(f"Strategy execution logged to {log_file}")
        except Exception as e:
            logger.error(f"Failed to log strategy execution: {e}")

    def get_execution_statistics(self) -> Dict:
        """Get execution statistics across all strategies"""
        return {
            'total_executions': len(self.execution_stats),
            'by_strategy': self.execution_stats,
            'last_updated': datetime.utcnow().isoformat()
        }

# Example usage
async def test_strategy_executor():
    """Test the unified strategy executor"""

    # Mock configuration
    config = {
        'risk_config': {
            'account_size': 10000,
            'max_daily_risk': 3.0
        }
    }

    executor = UnifiedStrategyExecutor(config)

    # Mock market data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1min')
    market_data = {
        'm15': pd.DataFrame({
            'Open': np.random.normal(1.1000, 0.001, 100),
            'High': np.random.normal(1.1005, 0.001, 100),
            'Low': np.random.normal(1.0995, 0.001, 100),
            'Close': np.random.normal(1.1000, 0.001, 100),
            'Volume': np.random.randint(100, 1000, 100)
        }, index=dates)
    }

    # Mock analysis result
    analysis_result = {
        'analysis': {
            'structure': {
                'htf_bias': 'Bullish',
                'choch_detected': True,
                'bos_detected': True,
                'confidence': 0.8
            },
            'liquidity': {
                'sweep_probability': 0.7,
                'vwap_levels': []
            },
            'smc': {
                'fvg_zones': [{'high': 1.1010, 'low': 1.1005, 'type': 'bullish'}],
                'order_blocks': []
            },
            'confluence': {
                'overall_confluence': 0.75,
                'rsi_confluence': 0.8
            }
        },
        'confluence_score': 0.75
    }

    # Test all strategies
    strategies = ['Inv', 'MAZ2', 'TMC', 'Mentfx']

    for strategy in strategies:
        print(f"\nTesting {strategy} strategy:")
        result = await executor.execute_strategy(strategy, market_data, analysis_result, "EURUSD")
        print(f"Status: {result['status']}")
        if result['status'] == 'ready':
            print(f"Entry: {result['entry_params']['entry_price']}")
            print(f"Direction: {result['entry_params']['direction']}")
            print(f"SL: {result['risk_params']['stop_loss']}")
            print(f"TP: {result['risk_params']['take_profit']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_strategy_executor())
