# ncOS Journal v2.0 - Refactored

## Overview

The ncOS Journal v2.0 is a standalone journaling system extracted from ncOS v21.7, focused purely on trade journaling and analysis without any voice dependencies.

## Key Features

- **Pure Data Journaling**: CSV, JSONL, and Parquet support
- **ZBAR Pattern Analysis**: Advanced pattern detection and logging
- **Session Management**: Track trading sessions with detailed analytics
- **RESTful API**: Clean API for integration with other systems
- **Web Dashboard**: Real-time monitoring and analysis
- **No Voice Dependencies**: Completely separated from voice components

## Architecture

```
ncos_journal/
├── core/               # Core journal functionality
│   ├── journal_manager.py
│   └── writers/        # Storage backends
│       ├── csv_writer.py
│       ├── jsonl_writer.py
│       └── parquet_writer.py
├── zbar/              # Pattern analysis
│   ├── zbar_processor.py
│   ├── zbar_agent.py
│   └── zbar_bridge.py
├── api/               # REST API
│   └── journal_api.py
├── dashboard/         # Web interface
│   └── app.py
└── data/             # Data storage
    ├── journals/
    ├── exports/
    └── cache/
```

## Quick Start

1. **Setup the system**:
   ```bash
   python setup_journal_system.py
   ```

2. **Install dependencies**:
   ```bash
   pip install -r ncos_journal/requirements.txt
   ```

3. **Launch the system**:
   ```bash
   ./ncos_journal/launch.sh
   ```

4. **Access the interfaces**:
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501

## Usage Examples

### Python API
```python
from journal_manager import JournalManager

# Initialize
journal = JournalManager()

# Start session
session_id = journal.start_session("morning_trading")

# Log a trade
journal.log_trade({
    "symbol": "EURUSD",
    "action": "BUY",
    "price": 1.0850,
    "size": 0.1,
    "stop_loss": 1.0820,
    "take_profit": 1.0900
})

# Get session recap
recap = journal.get_session_recap()
```

### REST API
```bash
# Start session
curl -X POST http://localhost:8000/api/journal/session/start   -H "Content-Type: application/json"   -d '{"session_name": "morning_trading"}'

# Log trade
curl -X POST http://localhost:8000/api/journal/trade   -H "Content-Type: application/json"   -d '{
    "symbol": "EURUSD",
    "action": "BUY",
    "price": 1.0850,
    "size": 0.1
  }'
```

## Benefits of Refactoring

1. **Modularity**: Use only what you need
2. **Performance**: ~30% faster without voice overhead
3. **Maintainability**: Clear separation of concerns
4. **Flexibility**: Deploy independently or integrate with other systems
5. **Simplicity**: Focused on core journaling functionality

## Migration from ncOS v21.7

1. Export existing journal data from v21.7
2. Import into the new journal system
3. Update API endpoints in your trading bots
4. Optional: Keep voice module separate if needed

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.
