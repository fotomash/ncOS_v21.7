
"""
NCOS v24.1 - Phoenix Unified Main Orchestrator
Consolidated trading system integrating all components
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import traceback
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('NCOS_v24.1')

class NCOSConfig:
    """Centralized configuration management for NCOS v24.1"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.configs = {}
        self.load_all_configs()

    def load_all_configs(self):
        """Load all configuration files"""
        config_files = {
            'strategy_rules': 'strategy_rules.json',
            'chart_config': 'chart_config.json',
            'risk_config': 'risk_config.json',
            'agents_config': 'agents_config.json',
            'system_config': 'system_config.json'
        }

        for key, filename in config_files.items():
            filepath = self.config_dir / filename
            try:
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        self.configs[key] = json.load(f)
                        logger.info(f"Loaded {key} from {filename}")
                else:
                    self.configs[key] = self.get_default_config(key)
                    self.save_config(key)
                    logger.warning(f"Created default {key} config")
            except Exception as e:
                logger.error(f"Failed to load {key}: {e}")
                self.configs[key] = self.get_default_config(key)

    def get_default_config(self, config_type: str) -> Dict:
        """Return default configuration for each type"""
        defaults = {
            'strategy_rules': {
                "Inv": [
                    {"source": "smc", "metric": "liq_sweep_detected", "condition": "equals", "value": True},
                    {"source": "macro", "metric": "risk_state", "condition": "equals", "value": "Risk ON"}
                ],
                "MAZ2": [
                    {"source": "smc", "metric": "fvg_quality", "condition": ">=", "value": 0.7},
                    {"source": "indicator", "name": "RSI_14", "metric": "value", "condition": "is_oversold", "value": 30}
                ],
                "TMC": [
                    {"source": "smc", "metric": "bos_confirmed", "condition": "equals", "value": True},
                    {"source": "indicator", "name": "ADX_14", "metric": "value", "condition": ">", "value": 25}
                ],
                "Mentfx": [
                    {"source": "indicator", "name": "DSS", "metric": "slope", "condition": "is_rising", "value": 0},
                    {"source": "smc", "metric": "engulfing_pattern", "condition": "equals", "value": True}
                ]
            },
            'chart_config': {
                "default_chart_settings": {
                    "visuals": {
                        "paper_bgcolor": "rgb(17,17,17)",
                        "plot_bgcolor": "rgb(17,17,17)",
                        "font_color": "white",
                        "grid_color": "rgba(180,180,180,0.1)"
                    },
                    "elements": {
                        "show_market_structure": True,
                        "show_liquidity_sweeps": True,
                        "show_wyckoff_phase": True,
                        "entry_marker_size": 12
                    }
                }
            },
            'risk_config': {
                "default_risk": {
                    "account_size": 10000,
                    "risk_percent": 1.0,
                    "max_risk_per_trade": 2.0,
                    "max_daily_drawdown": 3.0,
                    "tp_rr": 3.0,
                    "sl_buffer_pips": 1.0
                }
            },
            'agents_config': {
                "agents": {
                    "copilot": "PHOENIX_COPILOT",
                    "analyzer": "STRUCTURE_ANALYZER",
                    "wyckoff": "WYCKOFF_DETECTOR",
                    "liquidity": "LIQUIDITY_ENGINE",
                    "executor": "TRADE_EXECUTOR"
                }
            },
            'system_config': {
                "system": {
                    "version": "24.1.0",
                    "debug_mode": False,
                    "auto_trade": False,
                    "scan_interval": 300,
                    "max_concurrent_analysis": 5
                }
            }
        }
        return defaults.get(config_type, {})

    def save_config(self, config_type: str):
        """Save configuration to file"""
        filepath = self.config_dir / f"{config_type}.json"
        try:
            with open(filepath, 'w') as f:
                json.dump(self.configs[config_type], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {config_type}: {e}")

    def get(self, config_type: str, key: str = None, default=None):
        """Get configuration value"""
        config = self.configs.get(config_type, {})
        if key:
            return config.get(key, default)
        return config

class DataPipelineV24:
    """Unified data pipeline for NCOS v24.1"""

    def __init__(self, config: NCOSConfig):
        self.config = config
        self.data_cache = {}
        self.last_update = {}

    async def fetch_and_process(self, symbol: str, timeframes: List[str]) -> Dict:
        """Fetch and process data for multiple timeframes"""
        try:
            # This would integrate with the actual data fetchers
            logger.info(f"Fetching data for {symbol} across {timeframes}")

            # Simulate data processing
            processed_data = {}
            for tf in timeframes:
                # In real implementation, this would call the actual data pipeline
                processed_data[tf] = self._simulate_ohlc_data(symbol, tf)

            return {
                'status': 'success',
                'symbol': symbol,
                'data': processed_data,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Data pipeline error for {symbol}: {e}")
            return {'status': 'error', 'message': str(e)}

    def _simulate_ohlc_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Simulate OHLC data for testing"""
        periods = {'m1': 100, 'm5': 50, 'm15': 30, 'h1': 24, 'h4': 12}
        n = periods.get(timeframe, 50)

        dates = pd.date_range(end=datetime.utcnow(), periods=n, freq='1min')
        base_price = 1.1000 if 'EUR' in symbol else 2000.0

        data = {
            'Open': np.random.normal(base_price, base_price * 0.001, n),
            'High': np.random.normal(base_price * 1.001, base_price * 0.001, n),
            'Low': np.random.normal(base_price * 0.999, base_price * 0.001, n),
            'Close': np.random.normal(base_price, base_price * 0.001, n),
            'Volume': np.random.randint(100, 1000, n)
        }

        return pd.DataFrame(data, index=dates)

class AnalysisEngineV24:
    """Consolidated analysis engine for NCOS v24.1"""

    def __init__(self, config: NCOSConfig):
        self.config = config
        self.analyzers = {}
        self._initialize_analyzers()

    def _initialize_analyzers(self):
        """Initialize all analysis components"""
        self.analyzers = {
            'structure': self._analyze_market_structure,
            'wyckoff': self._analyze_wyckoff_phase,
            'liquidity': self._analyze_liquidity,
            'smc': self._analyze_smc_zones,
            'confluence': self._calculate_confluence
        }

    async def run_full_analysis(self, data: Dict, symbol: str) -> Dict:
        """Run comprehensive analysis on market data"""
        try:
            logger.info(f"Running full analysis for {symbol}")

            results = {}

            # Run all analyzers
            for analyzer_name, analyzer_func in self.analyzers.items():
                try:
                    results[analyzer_name] = await analyzer_func(data, symbol)
                except Exception as e:
                    logger.error(f"Analyzer {analyzer_name} failed: {e}")
                    results[analyzer_name] = {'error': str(e)}

            # Calculate overall confluence score
            confluence_score = self._calculate_overall_confluence(results)

            return {
                'status': 'success',
                'symbol': symbol,
                'analysis': results,
                'confluence_score': confluence_score,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Full analysis failed for {symbol}: {e}")
            return {'status': 'error', 'message': str(e)}

    async def _analyze_market_structure(self, data: Dict, symbol: str) -> Dict:
        """Analyze market structure (CHoCH, BOS, swings)"""
        # This would integrate with market_structure_analyzer_smc.py
        return {
            'htf_bias': 'Bullish',
            'structure_points': [],
            'choch_detected': False,
            'bos_detected': True,
            'confidence': 0.75
        }

    async def _analyze_wyckoff_phase(self, data: Dict, symbol: str) -> Dict:
        """Analyze Wyckoff phases"""
        # This would integrate with phase_detector_wyckoff_v1.py
        return {
            'current_phase': 'Accumulation Phase B',
            'phase_confidence': 0.80,
            'key_events': ['SC', 'AR'],
            'trend_direction': 'Bullish'
        }

    async def _analyze_liquidity(self, data: Dict, symbol: str) -> Dict:
        """Analyze liquidity zones and sweeps"""
        # This would integrate with liquidity engines
        return {
            'liquidity_sweeps': [],
            'vwap_levels': [],
            'poi_zones': [],
            'sweep_probability': 0.65
        }

    async def _analyze_smc_zones(self, data: Dict, symbol: str) -> Dict:
        """Analyze Smart Money Concepts zones"""
        # This would integrate with smc_enrichment_engine.py
        return {
            'order_blocks': [],
            'fvg_zones': [],
            'mitigation_zones': [],
            'smc_bias': 'Bullish'
        }

    async def _calculate_confluence(self, data: Dict, symbol: str) -> Dict:
        """Calculate confluence factors"""
        return {
            'rsi_confluence': 0.7,
            'volume_confluence': 0.6,
            'structure_confluence': 0.8,
            'overall_confluence': 0.7
        }

    def _calculate_overall_confluence(self, results: Dict) -> float:
        """Calculate overall confluence score from all analysis results"""
        scores = []
        for analyzer_result in results.values():
            if isinstance(analyzer_result, dict) and 'confidence' in analyzer_result:
                scores.append(analyzer_result['confidence'])

        return np.mean(scores) if scores else 0.0

class StrategyEngineV24:
    """Consolidated strategy engine for NCOS v24.1"""

    def __init__(self, config: NCOSConfig):
        self.config = config
        self.strategy_rules = config.get('strategy_rules')

    async def match_strategy(self, analysis_result: Dict) -> Dict:
        """Match current market conditions to best strategy"""
        try:
            best_strategy = None
            best_score = 0.0

            for strategy_name, rules in self.strategy_rules.items():
                score = self._evaluate_strategy_fit(analysis_result, rules)
                if score > best_score:
                    best_score = score
                    best_strategy = strategy_name

            threshold = 0.70
            if best_score >= threshold:
                return {
                    'strategy': best_strategy,
                    'confidence': best_score,
                    'status': 'match_found'
                }
            else:
                return {
                    'strategy': None,
                    'confidence': best_score,
                    'status': 'no_match'
                }

        except Exception as e:
            logger.error(f"Strategy matching failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _evaluate_strategy_fit(self, analysis: Dict, rules: List[Dict]) -> float:
        """Evaluate how well analysis fits strategy rules"""
        if not rules:
            return 0.0

        matches = 0
        total_rules = len(rules)

        for rule in rules:
            if self._check_rule(analysis, rule):
                matches += 1

        return matches / total_rules if total_rules > 0 else 0.0

    def _check_rule(self, analysis: Dict, rule: Dict) -> bool:
        """Check if a single rule condition is met"""
        try:
            source = rule.get('source')
            metric = rule.get('metric')
            condition = rule.get('condition')
            target = rule.get('value')

            # Get value from analysis based on source
            value = self._get_analysis_value(analysis, source, metric, rule.get('name'))

            if value is None:
                return False

            # Evaluate condition
            if condition == 'equals':
                return value == target
            elif condition == '>':
                return float(value) > float(target)
            elif condition == '<':
                return float(value) < float(target)
            elif condition == '>=':
                return float(value) >= float(target)
            elif condition == '<=':
                return float(value) <= float(target)
            # Add more conditions as needed

            return False

        except Exception as e:
            logger.debug(f"Rule check failed: {e}")
            return False

    def _get_analysis_value(self, analysis: Dict, source: str, metric: str, name: str = None):
        """Extract value from analysis result based on source and metric"""
        try:
            if source in analysis.get('analysis', {}):
                source_data = analysis['analysis'][source]
                if name and name in source_data:
                    return source_data[name].get(metric)
                return source_data.get(metric)
            return None
        except Exception:
            return None

class ExecutionEngineV24:
    """Consolidated execution engine for NCOS v24.1"""

    def __init__(self, config: NCOSConfig):
        self.config = config
        self.risk_config = config.get('risk_config', 'default_risk')

    async def execute_strategy(self, strategy_result: Dict, analysis_result: Dict, symbol: str) -> Dict:
        """Execute the matched strategy"""
        try:
            if strategy_result.get('status') != 'match_found':
                return {'status': 'no_execution', 'reason': 'No strategy match'}

            strategy_name = strategy_result['strategy']
            confidence = strategy_result['confidence']

            # Calculate entry parameters
            entry_params = self._calculate_entry_parameters(strategy_name, analysis_result, symbol)

            # Apply risk management
            risk_params = self._calculate_risk_parameters(entry_params)

            # Generate execution result
            execution_result = {
                'status': 'ready_for_execution',
                'strategy': strategy_name,
                'symbol': symbol,
                'confidence': confidence,
                'entry_price': entry_params.get('entry_price'),
                'stop_loss': risk_params.get('stop_loss'),
                'take_profit': risk_params.get('take_profit'),
                'position_size': risk_params.get('position_size'),
                'direction': entry_params.get('direction'),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Log the execution
            self._log_execution(execution_result)

            return execution_result

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _calculate_entry_parameters(self, strategy: str, analysis: Dict, symbol: str) -> Dict:
        """Calculate entry parameters based on strategy"""
        # This would integrate with entry_executor_smc.py logic
        base_price = 1.1000 if 'EUR' in symbol else 2000.0

        return {
            'entry_price': base_price * (1 + np.random.normal(0, 0.001)),
            'direction': 'buy' if np.random.random() > 0.5 else 'sell',
            'entry_reason': f'{strategy} setup confirmed'
        }

    def _calculate_risk_parameters(self, entry_params: Dict) -> Dict:
        """Calculate risk management parameters"""
        entry_price = entry_params.get('entry_price', 1.0)
        direction = entry_params.get('direction', 'buy')

        # Simple risk calculation
        risk_pct = self.risk_config.get('risk_percent', 1.0) / 100
        sl_buffer = entry_price * 0.01  # 1% buffer
        tp_ratio = self.risk_config.get('tp_rr', 3.0)

        if direction == 'buy':
            stop_loss = entry_price - sl_buffer
            take_profit = entry_price + (sl_buffer * tp_ratio)
        else:
            stop_loss = entry_price + sl_buffer
            take_profit = entry_price - (sl_buffer * tp_ratio)

        risk_amount = self.risk_config.get('account_size', 10000) * risk_pct
        position_size = risk_amount / sl_buffer

        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': round(position_size, 2),
            'risk_amount': risk_amount
        }

    def _log_execution(self, execution_result: Dict):
        """Log execution details"""
        log_dir = Path("journal")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"execution_{execution_result['symbol']}_{timestamp}.json"

        try:
            with open(log_file, 'w') as f:
                json.dump(execution_result, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")

class NCOSMainOrchestrator:
    """Main orchestrator for NCOS v24.1 Phoenix Unified"""

    def __init__(self, config_dir: str = "config"):
        self.config = NCOSConfig(config_dir)
        self.data_pipeline = DataPipelineV24(self.config)
        self.analysis_engine = AnalysisEngineV24(self.config)
        self.strategy_engine = StrategyEngineV24(self.config)
        self.execution_engine = ExecutionEngineV24(self.config)

        self.active_sessions = {}
        self.performance_stats = {}

        logger.info("NCOS v24.1 Phoenix Unified Orchestrator initialized")

    async def analyze_symbol(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """Perform complete analysis on a symbol"""
        if timeframes is None:
            timeframes = ['m15', 'h1', 'h4']

        try:
            logger.info(f"Starting analysis for {symbol}")

            # 1. Fetch and process data
            data_result = await self.data_pipeline.fetch_and_process(symbol, timeframes)
            if data_result['status'] != 'success':
                return data_result

            # 2. Run comprehensive analysis
            analysis_result = await self.analysis_engine.run_full_analysis(data_result['data'], symbol)
            if analysis_result['status'] != 'success':
                return analysis_result

            # 3. Match strategy
            strategy_result = await self.strategy_engine.match_strategy(analysis_result)

            # 4. Execute if strategy matched
            execution_result = None
            if strategy_result.get('status') == 'match_found':
                execution_result = await self.execution_engine.execute_strategy(
                    strategy_result, analysis_result, symbol
                )

            # 5. Compile final result
            final_result = {
                'status': 'success',
                'symbol': symbol,
                'timeframes': timeframes,
                'data_status': data_result['status'],
                'analysis': analysis_result,
                'strategy_match': strategy_result,
                'execution': execution_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            return final_result

        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            return {
                'status': 'error',
                'symbol': symbol,
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def run_market_scan(self, symbols: List[str]) -> Dict:
        """Run analysis on multiple symbols"""
        logger.info(f"Running market scan on {len(symbols)} symbols")

        results = {}
        tasks = []

        # Create analysis tasks
        for symbol in symbols:
            task = self.analyze_symbol(symbol)
            tasks.append(task)

        # Execute all tasks concurrently
        analysis_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Compile results
        for i, result in enumerate(analysis_results):
            symbol = symbols[i]
            if isinstance(result, Exception):
                results[symbol] = {
                    'status': 'error',
                    'message': str(result)
                }
            else:
                results[symbol] = result

        # Generate scan summary
        scan_summary = self._generate_scan_summary(results)

        return {
            'status': 'success',
            'scan_summary': scan_summary,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _generate_scan_summary(self, results: Dict) -> Dict:
        """Generate summary of scan results"""
        total_symbols = len(results)
        successful_analysis = sum(1 for r in results.values() if r.get('status') == 'success')
        strategy_matches = sum(1 for r in results.values() 
                             if r.get('strategy_match', {}).get('status') == 'match_found')
        execution_ready = sum(1 for r in results.values() 
                            if r.get('execution', {}).get('status') == 'ready_for_execution')

        return {
            'total_symbols': total_symbols,
            'successful_analysis': successful_analysis,
            'strategy_matches': strategy_matches,
            'execution_ready': execution_ready,
            'success_rate': round(successful_analysis / total_symbols * 100, 2) if total_symbols > 0 else 0,
            'match_rate': round(strategy_matches / successful_analysis * 100, 2) if successful_analysis > 0 else 0
        }

    async def start_monitoring(self, symbols: List[str], scan_interval: int = 300):
        """Start continuous monitoring of symbols"""
        logger.info(f"Starting continuous monitoring for {symbols} (interval: {scan_interval}s)")

        while True:
            try:
                scan_result = await self.run_market_scan(symbols)
                logger.info(f"Scan completed: {scan_result['scan_summary']}")

                # Wait for next scan
                await asyncio.sleep(scan_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

# Example usage and testing
async def main():
    """Main function for testing the orchestrator"""
    orchestrator = NCOSMainOrchestrator()

    # Test single symbol analysis
    result = await orchestrator.analyze_symbol("EURUSD")
    print("Single Symbol Analysis Result:")
    print(json.dumps(result, indent=2, default=str))

    # Test market scan
    symbols = ["EURUSD", "GBPUSD", "XAUUSD"]
    scan_result = await orchestrator.run_market_scan(symbols)
    print("\nMarket Scan Result:")
    print(json.dumps(scan_result['scan_summary'], indent=2))

if __name__ == "__main__":
    asyncio.run(main())
