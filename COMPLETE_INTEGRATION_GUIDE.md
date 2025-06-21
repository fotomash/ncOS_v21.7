# NCOS v21 Phoenix Mesh - Complete Integration Guide

## 🚀 Quick Start

### Step 1: Apply All Fixes
```bash
python fix_ncos_complete.py
```

### Step 2: Install Dependencies
```bash
pip install fastapi uvicorn pandas pydantic pyyaml python-dotenv
```

### Step 3: Start the System
```bash
python start_ncos.py
```

## 📦 Component Overview

### Enhanced Core Orchestrator
- **Purpose**: Central command processor with voice support
- **Features**:
  - Natural language command routing
  - Session management
  - ZBAR integration
  - Trade journaling
  - Voice tagging

### ZBAR Analysis System
- **Components**:
  - `zbar_agent.py` - Core analysis engine
  - `zbar_routes.py` - RESTful API endpoints
  - `ncos_zbar_api.py` - Complete API service
- **Features**:
  - Multi-timeframe analysis
  - Pattern recognition
  - Entry signal generation
  - Performance tracking

### Trading Agents
- **Quantitative Analyst**: Advanced market analysis
- **Market Maker**: Liquidity provision strategies
- **Data Retrieval**: Real-time data fetching

## 🎯 Usage Examples

### Voice Commands
```
# Start a trading session
ncos> session start

# Run ZBAR analysis
ncos> scan xauusd

# Tag a market observation
ncos> mark bullish gold h1

# Get session summary
ncos> session recap

# End session
ncos> session end
```

### API Usage

#### ZBAR Analysis Request
```bash
curl -X POST http://localhost:8001/strategy/zbar/execute_multi   -H "Content-Type: application/json"   -d '{
    "strategy": "zbar",
    "asset": "XAUUSD",
    "blocks": [{
      "id": "htf",
      "timeframe": "H4",
      "columns": ["time", "open", "high", "low", "close", "volume"],
      "data": [[...]]
    }],
    "context": {
      "initial_htf_bias": "bullish",
      "session_id": "london_2024"
    }
  }'
```

#### Query Journal
```bash
curl http://localhost:8001/journal/query?symbol=XAUUSD&limit=10
```

#### Get Statistics
```bash
curl http://localhost:8001/journal/stats
```

## 🏗️ System Architecture

```
NCOS v21 Phoenix Mesh
│
├── Orchestration Layer
│   ├── Enhanced Master Orchestrator
│   ├── Voice Command Router
│   └── Session Manager
│
├── Analysis Layer
│   ├── ZBAR Agent
│   ├── Quantitative Analyst
│   └── Pattern Recognition
│
├── API Layer
│   ├── Main API (Port 8000)
│   ├── ZBAR API (Port 8001)
│   └── WebSocket Support
│
└── Data Layer
    ├── Journal Manager
    ├── Session Storage
    └── Configuration
```

## 📊 Configuration

### Environment Variables (.env)
```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
ZBAR_PORT=8001

# Journal Settings
JOURNAL_PATH=data/zbar/trade_journal.jsonl

# Session Settings
DEFAULT_SESSION_TIMEOUT=24
MAX_SESSIONS=10

# Feature Flags
ENABLE_VOICE_COMMANDS=true
ENABLE_HOT_SWAP=true
```

### Enhanced Configuration (enhanced_config.yaml)
```yaml
system:
  name: NCOS v21 Phoenix Mesh
  version: 21.7
  enhanced_mode: true

zbar:
  enabled: true
  profiles:
    - htf_london
    - ny_session
    - asian_range

agents:
  quantitative_analyst:
    strategies: [wyckoff, smc, volume_profile]
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Add src to Python path
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Port Already in Use**
   ```bash
   # Find and kill process using port
   lsof -ti:8000 | xargs kill -9
   ```

3. **Missing Dependencies**
   ```bash
   # Install all requirements
   pip install -r requirements.txt
   ```

## 📈 Advanced Usage

### Custom Agent Profiles
Create new profiles in `config/agents/`:
```yaml
profile_name: scalping_profile
timeframes: [M1, M5]
indicators:
  - rsi
  - volume_profile
entry_rules:
  min_rr: 1.5
  max_spread: 2
```

### Extending Voice Commands
Add to `enhanced_core_orchestrator.py`:
```python
def route_command(self, prompt: str):
    # Add custom commands
    if "backtest" in prompt.lower():
        return self._run_backtest(prompt)
```

## 🚀 Production Deployment

### Using Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000 8001
CMD ["python", "start_ncos.py"]
```

### Using systemd
```ini
[Unit]
Description=NCOS Phoenix Mesh
After=network.target

[Service]
Type=simple
User=ncos
WorkingDirectory=/opt/ncos
ExecStart=/usr/bin/python3 /opt/ncos/start_ncos.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- ZBAR API Docs: http://localhost:8001/docs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

NCOS v21 Phoenix Mesh - Enhanced Edition
