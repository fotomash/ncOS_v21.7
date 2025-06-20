# NCOS v21 Complete Deployment Package

This package contains all components needed to run NCOS v21.

## Quick Start

1. Navigate to the repository directory (replace the path with your clone location):
   ```bash
   cd ncOS_v21.7
   ```

2. Run the deployment:
   ```bash
   ./scripts/deploy.sh
   ```

## Manual Start

1. Set Python path:
   ```bash
   export PYTHONPATH="${PWD}:${PWD}/agents:${PYTHONPATH}"
   ```

2. Run bootstrap:
   ```bash
cd scripts && python integration_bootstrap.py
```

## Environment Variables

Set API keys for external data sources before running the market data API:

```bash
export FINNHUB_API_KEY="your-finnhub-key"
export TWELVE_DATA_API_KEY="your-twelvedata-key"
```

## Running Tests

Install the project dependencies before executing the test suite. The tests rely
on `pandas`, `numpy` and all other packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

For additional test utilities install the development requirements as well:

```bash
pip install -r requirements-dev.txt
```

Then run the tests using `pytest`:

```bash
pytest
```

## Directory Structure

- `agents/` - All 13 agent implementations
- `config/` - Bootstrap and registry configurations. Individual agent
  configuration files named `<agent>_config.yaml` also live here
- `scripts/` - Integration bootstrap script
- `scripts/deploy.sh` - Quick deployment script

## Agents Included

1. MasterOrchestrator - System orchestration
2. VectorMemoryBoot - Memory management
3. ParquetIngestor - Data ingestion
4. DimensionalFold - Multi-dimensional analysis
5. MarketConditioner - Market condition evaluation
6. SignalProcessor - Signal processing
7. StrategyEvaluator - Strategy evaluation
8. PositionManager - Position management
9. RiskAnalyzer - Risk analysis
10. MetricsAggregator - Metrics collection
11. SMCRouter - Smart routing
12. MAZ2Executor - MAZ2 execution
13. TMCExecutor - TMC execution
14. LiquiditySniperAgent - Liquidity sweep detection
15. EntryExecutorSMCAgent - Executes precision entries

## Notes

- ParquetIngestor runs in stub mode if pandas/pyarrow not installed
- All agents are production-ready with circuit breakers
- Logs are written to JSON format in the logs directory
- `start_ncos.sh` and `status_ncos.sh` are created by `scripts/deploy.sh`; run the deployment before using them

---
### Market Manipulation Detection Module

This module provides real-time detection of market manipulation patterns, focusing on spread manipulation and quote stuffing for XAUUSD.

**Core Components:**
- **MarketManipulationAgent:** Ingests real-time tick data and applies configurable rules to detect anomalies.
- **RiskMonitorAgent:** Subscribes to detection events and executes predefined risk management actions based on severity.
- **ComplianceAgent:** Provides automated logging of all detected events for regulatory and audit purposes.

**Configuration:**
- The module's behavior is controlled by `config/xauusd_manipulation_config.yaml`.
- Enable or disable agents in `config/agent_registry.yaml`.

## Semantic Utility Functions

The `ncOS.semantic_utils` module provides helper functions for common runtime tasks:

- **extract_and_validate_uploaded_archive** - Extracts an uploaded archive and validates its format.
- **summarize_workspace_memory** - Produces a quick summary of processed files, active agents and memory usage.
- **intelligently_route_user_request_to_best_agent** - Selects the most suitable agent for a request based on type or intent.
- **automatically_optimize_memory_and_consolidate_session_data** - Trims session data and clamps memory usage to configured limits.
- **detect_and_recover_from_system_errors_automatically** - Attempts basic recovery steps for common system errors.

Example usage:

```python
import asyncio
from types import SimpleNamespace
from ncOS.semantic_utils import summarize_workspace_memory

state = SimpleNamespace(memory_usage_mb=128.5, processed_files=["log.txt"], active_agents=["risk"])

summary = asyncio.run(summarize_workspace_memory(state))
print(summary)
```

## Predictive Engine

NCOS includes an optional predictive engine that scores every trade setup using
a seven-factor model. Setups are graded from **A** to **D**, enabling the system
to filter low-quality trades and adjust risk dynamically. Detailed
documentation can be found in
[PREDICTIVE_ENGINE_GUIDE.md](to_integrate/PREDICTIVE_ENGINE_GUIDE.md).

To validate your environment and run a quick backtest, execute:

```bash
python scripts/quick_start_predictive.py
```

## Fractal and Structure Analysis

The `add_structure.py` script computes fractal highs/lows and a simple market
structure label from any CSV file containing `Open`, `High`, `Low` and `Close`
columns. The resulting file includes `fractal_high`, `fractal_low` and
`structure` columns.

Example usage:

```bash
python -m scripts.add_structure data/price_data.csv -o data/price_with_structure.csv
```

## Contributing

For guidelines on submitting issues and pull requests, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Running `add_structure.py`

The optional `add_structure.py` script enriches OHLCV CSV files with three new
columns that describe market structure:

- `fractal_high` – marks rows where a high fractal occurs
- `fractal_low` – marks rows where a low fractal occurs
- `structure` – the resulting market bias (bullish, bearish or neutral)

Invoke the script with the path to your input data and an output location:

```bash
python add_structure.py --input data/ohlcv.csv --output data/ohlcv_with_structure.csv
```

After execution, the output CSV will include the three columns above alongside
your original OHLCV data.

## Trading Disclaimer

**Trading Disclaimer**: This system is for educational and research purposes. Trading involves risk of financial loss. Past performance does not guarantee future results. Always test thoroughly before live trading.

