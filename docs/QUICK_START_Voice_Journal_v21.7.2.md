# NCOS Voice Journal - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Download Files
Get these files from the implementation:
- `voice_tag_parser.py`
- `zbar_voice_integration.py`
- `menu_voice_integration.py`
- `voice_api_routes.py`
- `voice_command_dashboard.py`

### 2. Install Dependencies
```bash
pip install fastapi uvicorn streamlit pandas pyyaml requests
```

### 3. Create Folders
```bash
mkdir -p logs config api dashboard core
```

### 4. Start System
```bash
# Terminal 1: API Server
python api/main.py

# Terminal 2: Dashboard  
streamlit run dashboard/voice_command_dashboard.py

# Terminal 3: Voice Interface
python ncos_voice/ncos_voice_unified.py
```

## 🎤 First Commands

Try these voice commands:
1. `mark gold bullish h4`
2. `check all setups`
3. `analyze xauusd m15`

## 📊 View Results

1. Open browser to `http://localhost:8501`
2. Filter by session or symbol
3. Click any entry to expand
4. Use "Re-run Strategy" button

That's it! You're now tracking trades with voice commands.

---

## Common Voice Commands

### Marking Trades
- `mark [symbol] [bias] on [timeframe]`
- `log [symbol] [action] at [price]`

### Analysis
- `analyze [symbol] [timeframe]`
- `run zbar on [symbol]`

### Queries
- `show all [bias] trades`
- `check [session] setups`
- `find high maturity trades`

### Examples
- `mark gold bullish h4 london session`
- `analyze eurusd 15 minute`
- `check all trades today`
