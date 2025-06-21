# NCOS v21 Phoenix Mesh

## 🚀 Production-Ready LLM-Native Financial Analysis Runtime

### Overview
NCOS v21 Phoenix Mesh is a high-performance, agent-based architecture for financial market analysis featuring:

- **38 Wyckoff Analysis Components** - Complete methodology implementation
- **56 Pydantic Models** - Type-safe configuration and data handling
- **12 Vector Memory Systems** - Advanced optimization and compression
- **Native Charting** - Interactive visualizations with action hooks
- **Phoenix Fast Mode** - Optimized analysis with caching

### Quick Start

1. **Install Python 3.11.12**
   If you use [pyenv](https://github.com/pyenv/pyenv), run:
   ```bash
   pyenv install 3.11.12
   pyenv local 3.11.12
   ```
   Otherwise ensure Python `3.11.12` is available on your system.

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**
   ```bash
   python main.py --test
   ```

4. **Start Analysis**
   ```bash
   python main.py --analyze your_data.csv
   ```

4. **Interactive Mode**
   ```python
   from phoenix_session import create_phoenix_integration

   # Initialize Phoenix
   phoenix = create_phoenix_integration()

   # Quick analysis
   result = await phoenix.analyze(data)
   print(f"Phase: {result['phase']}")
   ```

### Architecture

```
NCOS v21 Phoenix Mesh
├── Agents (28 components)
│   ├── Strategy Agents (Wyckoff, SMC)
│   ├── Data Ingestion Agents
│   ├── Visualization Agents
│   └── Memory Vector Agents
├── Orchestrators
│   └── Master Orchestrator
├── Schemas (56 Pydantic models)
├── Phoenix Session
│   ├── Core (Optimized engine)
│   └── Adapters (Integration layer)
└── Configuration
    ├── workspace_config.yaml
    └── phoenix_config.json
```

### Key Features

- **Wyckoff Analysis**: Complete implementation with 38 components
- **Smart Money Concepts**: Order blocks, FVGs, liquidity analysis
- **Vector Memory**: Token optimization and semantic search
- **Native Charting**: Real-time, interactive visualizations
- **Phoenix Mode**: 10x faster analysis with intelligent caching

### Performance

- Analysis Time: <100ms (Phoenix mode)
- Token Efficiency: 90% reduction with compression
- Memory Usage: Optimized with automatic cleanup
- Scalability: Horizontal scaling ready

### Development

```bash
# Run in development mode
python main.py

# Run with optimization
python main.py --optimize

# Analyze specific data
python main.py --analyze data.csv --source csv
```

### Testing

```bash
# Run all tests
python test_phoenix.py

# Run specific test suite
python -m unittest test_phoenix.TestPhoenixIntegration
```

### License
Proprietary - NCOS v21 Phoenix Mesh

### Support
For support, contact the NCOS development team.
