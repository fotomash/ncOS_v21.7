# NCOS v21 Production System

## Overview

NCOS (Neural Computation Operating System) v21 is a production-ready financial data processing and trading system
featuring 13 specialized agents working in a coordinated mesh architecture.

## Quick Start

1. Extract the package:
   ```bash
   tar -xzf ncos_v21_production_candidate.tar.gz
   cd ncOS_v21.7
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start system:
   ```bash
   python start_ncos.py
   ```

## Components

- 13 Core Agents (see agent_registry.yaml)
- Single-session architecture
- Lightweight vector memory
- Dual execution strategies (MAZ2/TMC)
- Comprehensive risk management

## Environment Variables

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for the full list of
supported variables and defaults. At a minimum you should provide API keys:

```
export FINNHUB_API_KEY="<your-finnhub-key>"
export TWELVE_DATA_API_KEY="<your-twelvedata-key>"
```

## Testing

- Unit tests: python -m unittest tests.test_ncos_agents
- Integration tests: python tests/integration_tests.py

## Support

For issues or questions, refer to the documentation in the docs/ directory.
