# 🚀 NCOS v21.7.1 Phoenix Mesh - Complete AI Trading Ecosystem

[![Version](https://img.shields.io/badge/version-21.7.1-blue.svg)](https://github.com/ncos/phoenix-mesh)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/ncos/phoenix-mesh)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Neural Cognitive Operating System (NCOS) v21.7.1 Phoenix Mesh** is a comprehensive AI-powered trading ecosystem that combines advanced market analysis, multi-agent orchestration, and intelligent workflow management for institutional-grade trading operations.

## 🎯 **System Overview**

NCOS v21.7.1 represents the most advanced iteration of the Neural Cognitive Operating System, featuring:

- **🔥 12 Specialized Trading Agents** with priority-based coordination
- **📊 Native Vector Processing** for 10x faster market data analysis
- **🔄 Zanflow Orchestration** with advanced workflow management
- **🧠 Knowledge Intelligence** with asset detection and retrieval
- **💬 Enhanced User Interaction** with dynamic menus and conversation flow
- **📈 6 Advanced Trading Strategies** covering SMC, Wyckoff, and Orderflow analysis
- **🎯 8 Intelligent Triggers** for comprehensive system coordination

## 🏗️ **Architecture**

### **Core System Components**

```
NCOS v21.7.1 Phoenix Mesh Architecture
├── Core Orchestration Layer (Priority 1-2)
│   ├── Master Orchestrator (Enhanced)
│   └── Session State Manager (Enhanced)
├── Specialized Enhancement Layer (Priority 3-6)
│   ├── Zanflow Orchestrator
│   ├── Vector Data Processor
│   ├── Knowledge Intelligence Agent
│   └── Interaction Manager
└── Trading Strategy Layer (Priority 7-12)
    ├── SMC Liquidity Trap Agent
    ├── Wyckoff Phase Cycle Agent
    ├── Session Sweep Reversal Agent
    ├── Micro Wyckoff Event Agent
    ├── Orderflow Anomaly Agent
    └── Protection Reentry Agent
```

### **Data Processing Pipeline**

```
Market Data → Vector Processor → Strategy Agents → Risk Guardian → Execution
     ↓              ↓                    ↓             ↓           ↓
Knowledge Base → Intelligence → Workflow → Triggers → State Manager
```

## 🚀 **Quick Start**

### **Prerequisites**
 - Python 3.10+
- Redis (for L1 memory)
- PostgreSQL with pgvector (for L3 memory)
- FAISS (for L2 vector similarity)

### **Installation**
```bash
# Clone the repository
git clone https://github.com/ncos/phoenix-mesh.git
cd phoenix-mesh

# Install dependencies
pip install -r requirements.txt

# Initialize the system
python setup.py install
```

### **Basic Launch**
```bash
# Launch complete NCOS v21.7.1 system
python -m ncos.agents.master_orchestrator \
  --mode=enhanced_trading \
  --components=all \
  --strategies=all \
  --action=start_session
```

### **Component-Specific Launch**
```bash
# Launch with specific components
python -m ncos.agents.master_orchestrator \
  --mode=trading \
  --enable_vector_processing \
  --enable_zanflow_orchestration \
  --enable_knowledge_intelligence \
  --strategies=smc,wyckoff,session_sweep
```

## 🎯 **Trading Strategies**

### **1. SMC Liquidity Trap Agent**
- **Focus**: Engineered liquidity exploitation with tick validation
- **Timeframes**: M1, M5
- **Risk Profile**: Aggressive (2.5% per trade)
- **Features**: Liquidity hunting, trap reversal detection

### **2. Wyckoff Phase Cycle Agent**
- **Focus**: Phase transition analysis for trend plays
- **Timeframes**: H1, M15, M5
- **Risk Profile**: Conservative (1.5% per trade)
- **Features**: Accumulation/distribution detection, phase analysis

### **3. Session Sweep Reversal Agent**
- **Focus**: Session-based sweep and reversal trading
- **Timeframes**: M5, M1
- **Risk Profile**: Moderate (2% per trade)
- **Features**: Kill zone awareness, session timing

### **4. Micro Wyckoff Event Agent**
- **Focus**: Tick-level precision analysis with event scoring
- **Timeframes**: Tick, M1
- **Risk Profile**: Precision (1% per trade)
- **Features**: Micro-structure analysis, event scoring

### **5. Orderflow Anomaly Agent**
- **Focus**: Volume/orderflow anomaly detection and filtering
- **Timeframes**: M1, M5
- **Risk Profile**: Defensive (1.5% per trade)
- **Features**: Volume spike detection, orderflow analysis

### **6. Protection Reentry Agent**
- **Focus**: Advanced risk management with reentry logic
- **Timeframes**: M1, M5
- **Risk Profile**: Protective (1% per trade)
- **Features**: Stop loss management, reentry optimization

## 🔧 **Configuration**

### **Agent Registry Configuration**
```yaml
# configs/agent_registry.yaml
enhanced_ncos_agents:
  master_orchestrator:
    class: "MasterOrchestrator"
    priority: 1
    enhancements: ["zanflow_integration", "vector_data_access"]

  zanflow_orchestrator:
    class: "ZanflowOrchestratorAgent"
    priority: 3
    capabilities: ["prompt_engineering", "logical_blocks"]
```

### **Strategy Configuration**
```yaml
# config/strategies/smc_liquidity_trap.yaml
strategy:
  name: "SMC Liquidity Trap"
  risk_per_trade: "2.5%"
  max_positions: 2
  timeframes: ["M1", "M5"]
  triggers: ["liquidity_trap_detected"]
```

### **Trigger Routes Configuration**
```yaml
# configs/trigger_routes.yaml
triggers:
  market_data_update:
    priority: 1
    route_to: ["vector_data_processor", "smc_master_agent"]
    actions: ["process_vector_data", "trigger_strategy_analysis"]
```

## 📊 **System Features**

### **Native Vector Processing**
- **10x Performance**: Native vector operations for market data
- **Real-time Search**: Pattern matching and similarity search
- **Optimized Storage**: Efficient vector indexing and retrieval

### **Zanflow Orchestration**
- **Workflow Management**: Advanced logical block processing
- **Prompt Engineering**: Intelligent prompt generation and optimization
- **Structural Flow**: Dynamic workflow execution and management

### **Knowledge Intelligence**
- **Asset Detection**: Automatic asset classification and detection
- **Knowledge Retrieval**: Context-aware information retrieval
- **Intelligent Search**: Semantic search across knowledge base

### **Enhanced Interaction**
- **Dynamic Menus**: Context-aware menu generation
- **Conversation Flow**: Intelligent conversation management
- **Response Templates**: Optimized response generation

## 🛡️ **Risk Management**

### **Multi-Layer Risk Protection**
- **Per-Strategy Limits**: Individual risk allocation per strategy
- **Portfolio Protection**: Overall portfolio risk monitoring
- **Real-time Monitoring**: Continuous risk assessment
- **Auto-Recovery**: Automatic system recovery mechanisms

### **Risk Allocation**
```
Total System Risk Allocation: ~9%
├── SMC Liquidity Trap: 2.5% (Aggressive)
├── Wyckoff Phase Cycle: 1.5% (Conservative)
├── Session Sweep Reversal: 2% (Moderate)
├── Micro Wyckoff Event: 1% (Precision)
├── Orderflow Anomaly: 1.5% (Defensive)
└── Protection Reentry: 1% (Protective)
```

## 📈 **Performance Metrics**

### **System Performance**
- **Data Processing**: 10x faster with native vector operations
- **Strategy Execution**: Sub-second signal generation
- **Risk Monitoring**: Real-time risk assessment
- **Memory Efficiency**: Optimized multi-tier memory system

### **Trading Performance**
- **Multi-Timeframe**: Tick to H1 analysis coverage
- **Strategy Diversity**: 6 complementary trading approaches
- **Risk-Adjusted**: Optimized risk/reward ratios
- **Session Awareness**: Kill zone and session timing

## 🔄 **System Monitoring**

### **Health Checks**
```bash
# System health validation
python -c "from agents.master_orchestrator import MasterOrchestrator; MasterOrchestrator().validate_system()"

# Agent status check
python -c "from agents.risk_guardian import RiskGuardian; RiskGuardian().system_status()"
```

### **Performance Monitoring**
- **Agent Performance**: Individual agent metrics
- **Strategy Performance**: Trading strategy analytics
- **System Resources**: Memory and CPU utilization
- **Risk Metrics**: Real-time risk monitoring

## 📚 **Documentation**

### **Configuration Files**
- `configs/agent_registry.yaml` - Agent definitions and priorities
- `configs/strategy_profiles.json` - Trading strategy configurations
- `configs/trigger_routes.yaml` - Trigger routing and priorities
- `configs/system_config.json` - System-wide configuration

### **Agent Documentation**
- `docs/agents/` - Individual agent documentation
- `docs/strategies/` - Trading strategy guides
- `docs/workflows/` - Zanflow workflow documentation
- `docs/api/` - API reference documentation

## 🤝 **Contributing**

We welcome contributions to NCOS v21.7.1! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Development installation
pip install -e .[dev]

# Run tests
pytest tests/

# Code formatting
black ncos/
flake8 ncos/
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: [docs.ncos.ai](https://docs.ncos.ai)
- **Issues**: [GitHub Issues](https://github.com/ncos/phoenix-mesh/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ncos/phoenix-mesh/discussions)
- **Email**: support@ncos.ai

## 🎯 **Roadmap**

### **v21.8.0 (Planned)**
- Enhanced machine learning integration
- Advanced backtesting capabilities
- Extended asset class support
- Performance optimizations

### **v22.0.0 (Future)**
- Multi-broker integration
- Advanced portfolio management
- Real-time collaboration features
- Cloud deployment options

---

**NCOS v21.7.1 Phoenix Mesh - Powering the Future of AI Trading** 🚀

*Built with ❤️ by the NCOS Team*
