# NCOS v11.5 Phoenix - Complete Implementation Package

## 🚀 Overview
This package contains the complete implementation of NCOS v11.5 Phoenix, featuring a Neural Agent Mesh architecture with single-session LLM runtime and multi-agent virtualization.

### Key Features
- **Neural Agent Mesh**: Multi-agent virtualization in single LLM session
- **Token Budget Management**: Automatic compression and optimization (128k tokens)
- **Vector Memory**: FAISS-based with session persistence
- **Pydantic v2 Schemas**: Type-safe configuration and validation
- **Hot-swappable Agents**: Runtime agent loading and management

## 📁 Package Structure
```
ncos_v11_5_complete_package/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main.py                      # Application entry point
├── src/                         # Source code
│   ├── master_orchestrator.py   # Core orchestrator
│   ├── schemas/                 # Pydantic models
│   ├── mesh/                    # Neural mesh implementation
│   ├── pipeline/                # Processing pipeline
│   ├── memory/                  # Vector memory system
│   ├── agents/                  # Agent implementations
│   └── utils/                   # Utilities
├── config/                      # Configuration files
│   ├── phoenix.yaml            # Main configuration
│   └── agents/                 # Agent profiles
├── docs/                       # Documentation
│   ├── architecture.md         # System architecture
│   ├── migration_guide.md      # Migration from v11
│   ├── api_reference.md        # API documentation
│   └── deployment.md           # Deployment guide
├── tests/                      # Test suite
├── examples/                   # Usage examples
└── metadata/                   # System metadata
```

## 🚀 Quick Start

### 1. Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Edit `config/phoenix.yaml` to configure:
- LLM provider and API keys
- Token budget limits
- Vector memory settings
- Agent profiles to load

### 3. Run the System
```bash
# Basic startup
python main.py

# With custom config
python main.py --config config/custom.yaml

# Development mode
python main.py --dev --reload
```

## 🏗️ Architecture Overview

### Neural Agent Mesh
The system virtualizes multiple specialized agents within a single LLM session:
- **Token Budget**: 128k tokens with automatic compression at 80% usage
- **Pipeline Stages**: 6-stage processing pipeline
- **Memory Tiers**: L1 (Redis), L2 (FAISS), L3 (PostgreSQL)

### Core Components
1. **Master Orchestrator**: Central coordination and session management
2. **Mesh Kernel**: Agent virtualization and routing
3. **Pipeline Stages**: Modular processing stages
4. **Vector Memory**: Persistent memory with similarity search
5. **Budget Manager**: Token usage tracking and compression

## 📊 Agent Profiles

### Trading Strategy Agents
- **MacroAnalyser**: Macroeconomic context analysis
- **HTFAnalyst**: Higher timeframe structure validation
- **RiskManager**: Position sizing and risk management
- **EntryExecutorSMC**: Smart Money Concept entry execution
- **TradeJournalist**: Trade logging and performance analytics

### System Agents
- **MomentumDetector**: Market momentum analysis
- **SpoofingDetector**: Market manipulation detection
- **LiquidityAnalyser**: Liquidity zone identification

## 🔄 Migration from NCOS v11

See `docs/migration_guide.md` for detailed migration instructions. Key changes:
- Pydantic v2 schemas (breaking changes)
- Single-session architecture
- New configuration format
- Updated agent profiles

## 🧪 Testing
```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_schemas.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📈 Performance Benchmarks
- Token usage: ~63k/128k for full pipeline
- Processing time: <500ms per request
- Memory usage: <1GB with 10k vectors
- Concurrent sessions: 100+ supported

## 🚢 Deployment
See `docs/deployment.md` for production deployment guide.

### Docker
```bash
docker build -t ncos-phoenix:v11.5 .
docker run -p 8000:8000 ncos-phoenix:v11.5
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

## 📝 License
MIT License - see LICENSE file for details.

## 🤝 Contributing
See CONTRIBUTING.md for contribution guidelines.

## 📞 Support
- Documentation: `docs/`
- Issues: GitHub Issues
- Email: support@ncos.ai

---
Built with ❤️ by the NCOS Team
