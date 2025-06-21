# NCOS v21 Phoenix Mesh - Quick Start Guide

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv ncos_env
source ncos_env/bin/activate  # On Windows: ncos_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy example configuration
cp config/workspace_config.yaml config/local_config.yaml

# Edit configuration
# - Set API endpoints
# - Configure data sources
# - Adjust memory limits
```

### 3. Initialize System
```python
from orchestrators.master import MasterOrchestrator
from config import load_config

# Load configuration
config = load_config('config/local_config.yaml')

# Initialize orchestrator
orchestrator = MasterOrchestrator(config)
await orchestrator.initialize()

# System is ready!
```

### 4. Run Wyckoff Analysis
```python
from strategies.wyckoff import WyckoffAnalyzer

# Create analyzer
analyzer = WyckoffAnalyzer(config.strategies.wyckoff)

# Analyze market data
phase = analyzer.detect_phase(market_data)
micro_structure = analyzer.analyze_micro_structure(market_data)

print(f"Current Phase: {phase}")
print(f"Micro Analysis: {micro_structure}")
```

### 5. Enable Native Charting
```python
from visualization.chart_engine import NativeChartEngine

# Initialize chart engine
chart_engine = NativeChartEngine(config.charting)

# Create chart with action hooks
chart = chart_engine.create_chart(
    data=market_data,
    chart_type='candlestick',
    action_hooks=['zoom', 'annotate', 'export']
)

# Render chart
chart.render('output/analysis.html')
```

## 📊 Key Features

### Memory Management
- **L1 Session**: 8192 token budget per session
- **L2 Vector**: 75% compression ratio
- **L3 Persistent**: SQLite backend with 2GB cache

### Agent Architecture
- Hot-swappable agents
- Namespace isolation
- Single-session safety

### Financial Analysis
- 38 Wyckoff components
- SMC (Smart Money Concepts)
- Liquidity detection
- Risk management

## 🔧 Troubleshooting

### Common Issues

1. **Token Budget Exceeded**
   ```python
   # Monitor token usage
   session_state = orchestrator.get_session_state(session_id)
   print(f"Tokens used: {session_state.token_used}/{session_state.token_budget}")
   ```

2. **Memory Limit Reached**
   ```python
   # Check memory usage
   memory_stats = orchestrator.get_memory_stats()
   for namespace, usage in memory_stats.items():
       print(f"{namespace}: {usage}MB")
   ```

3. **Agent Not Responding**
   ```python
   # Health check
   health = await orchestrator.health_check()
   for agent, status in health.items():
       print(f"{agent}: {status}")
   ```

## 📚 Further Reading
- Architecture Document: `NCOS_v21_ARCHITECTURE.md`
- Migration Guide: `MIGRATION_MATRIX.json`
- API Reference: `docs/api_reference.md`
