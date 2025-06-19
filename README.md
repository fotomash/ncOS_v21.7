# NCOS v21 Complete Deployment Package

This package contains all components needed to run NCOS v21.

## Quick Start

1. Navigate to the repository directory:
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

## Directory Structure

- `agents/` - All 13 agent implementations
- `config/` - Bootstrap and registry configurations  
- `scripts/` - Integration bootstrap script
- `deploy.sh` - Quick deployment script

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

## Notes

- ParquetIngestor runs in stub mode if pandas/pyarrow not installed
- All agents are production-ready with circuit breakers
- Logs are written to JSON format in the logs directory
- `start_ncos.sh` and `status_ncos.sh` are created by `scripts/deploy.sh`; run the deployment before using them
