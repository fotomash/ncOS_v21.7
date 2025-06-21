import os
from pathlib import Path

# Create directory structure
directories = ['api', 'dashboard', 'data', 'logs']
for dir_name in directories:
    Path(dir_name).mkdir(exist_ok=True)
    print(f"✅ Created directory: {dir_name}")

# Now create the fixed main.py
fixed_main_py = '''"""
ncOS Journal API - Phoenix Edition
Focused on journaling without voice dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="ncOS Journal API",
    description="Trading journal and analysis API",
    version="21.7"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TradeEntry(BaseModel):
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None
    patterns: Optional[List[str]] = []
    session_id: Optional[str] = None
    trace_id: Optional[str] = None

class JournalEntry(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []
    timestamp: Optional[str] = None

class AnalysisEntry(BaseModel):
    symbol: str
    analysis_type: str
    content: Dict[str, Any]
    timestamp: Optional[str] = None

# Data storage paths
DATA_DIR = Path("../data")
TRADES_FILE = DATA_DIR / "trades.jsonl"
JOURNAL_FILE = DATA_DIR / "journal.jsonl"
ANALYSIS_FILE = DATA_DIR / "analysis.jsonl"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Helper functions
def append_jsonl(file_path: Path, data: dict):
    """Append data to JSONL file"""
    with open(file_path, 'a') as f:
        f.write(json.dumps(data) + '\\n')

def read_jsonl(file_path: Path) -> List[dict]:
    """Read all entries from JSONL file"""
    if not file_path.exists():
        return []
    
    entries = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

# API Routes
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "ncOS Journal API - Phoenix Edition",
        "version": "21.7",
        "endpoints": {
            "trades": "/trades",
            "journal": "/journal",
            "analysis": "/analysis",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_files": {
            "trades": TRADES_FILE.exists(),
            "journal": JOURNAL_FILE.exists(),
            "analysis": ANALYSIS_FILE.exists()
        }
    }

# Trade endpoints
@app.post("/trades")
def create_trade(trade: TradeEntry):
    """Create a new trade entry"""
    trade_data = trade.dict()
    trade_data["timestamp"] = trade_data.get("timestamp") or datetime.now().isoformat()
    trade_data["id"] = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    append_jsonl(TRADES_FILE, trade_data)
    return {"message": "Trade created", "id": trade_data["id"]}

@app.get("/trades")
def get_trades(symbol: Optional[str] = None, session_id: Optional[str] = None):
    """Get all trades with optional filtering"""
    trades = read_jsonl(TRADES_FILE)
    
    if symbol:
        trades = [t for t in trades if t.get("symbol") == symbol]
    
    if session_id:
        trades = [t for t in trades if t.get("session_id") == session_id]
    
    return {"trades": trades, "count": len(trades)}

# Journal endpoints
@app.post("/journal")
def create_journal_entry(entry: JournalEntry):
    """Create a new journal entry"""
    entry_data = entry.dict()
    entry_data["timestamp"] = entry_data.get("timestamp") or datetime.now().isoformat()
    entry_data["id"] = f"journal_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    append_jsonl(JOURNAL_FILE, entry_data)
    return {"message": "Journal entry created", "id": entry_data["id"]}

@app.get("/journal")
def get_journal_entries(category: Optional[str] = None, limit: int = 100):
    """Get journal entries with optional filtering"""
    entries = read_jsonl(JOURNAL_FILE)
    
    if category:
        entries = [e for e in entries if e.get("category") == category]
    
    # Sort by timestamp (newest first) and limit
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    entries = entries[:limit]
    
    return {"entries": entries, "count": len(entries)}

# Analysis endpoints
@app.post("/analysis")
def create_analysis(analysis: AnalysisEntry):
    """Create a new analysis entry"""
    analysis_data = analysis.dict()
    analysis_data["timestamp"] = analysis_data.get("timestamp") or datetime.now().isoformat()
    analysis_data["id"] = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    append_jsonl(ANALYSIS_FILE, analysis_data)
    return {"message": "Analysis created", "id": analysis_data["id"]}

@app.get("/analysis")
def get_analysis(symbol: Optional[str] = None, analysis_type: Optional[str] = None):
    """Get analysis entries with optional filtering"""
    analyses = read_jsonl(ANALYSIS_FILE)
    
    if symbol:
        analyses = [a for a in analyses if a.get("symbol") == symbol]
    
    if analysis_type:
        analyses = [a for a in analyses if a.get("analysis_type") == analysis_type]
    
    return {"analyses": analyses, "count": len(analyses)}

# Statistics endpoint
@app.get("/stats")
def get_statistics():
    """Get journal statistics"""
    trades = read_jsonl(TRADES_FILE)
    journal_entries = read_jsonl(JOURNAL_FILE)
    analyses = read_jsonl(ANALYSIS_FILE)
    
    # Calculate trade statistics
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.get("exit_price", 0) > t.get("entry_price", 0))
    
    # Get unique symbols
    symbols = list(set(t.get("symbol", "") for t in trades if t.get("symbol")))
    
    # Get pattern statistics
    all_patterns = []
    for trade in trades:
        all_patterns.extend(trade.get("patterns", []))
    
    pattern_counts = {}
    for pattern in all_patterns:
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    return {
        "trades": {
            "total": total_trades,
            "winning": winning_trades,
            "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0
        },
        "journal_entries": len(journal_entries),
        "analyses": len(analyses),
        "symbols": symbols,
        "patterns": pattern_counts,
        "last_update": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''

# Save the fixed main.py
with open('api/main.py', 'w') as f:
    f.write(fixed_main_py)
print("✅ Created: api/main.py")

# Create the dashboard app.py
dashboard_app = '''"""
ncOS Journal Dashboard - Phoenix Edition
"""

import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

# Configuration
API_URL = "http://localhost:8001"

# Page config
st.set_page_config(
    page_title="ncOS Journal - Phoenix Edition",
    page_icon="📊",
    layout="wide"
)

# Helper functions
def fetch_data(endpoint: str, params: dict = None) -> dict:
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params)
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return {}

def post_data(endpoint: str, data: dict) -> dict:
    """Post data to API"""
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data)
        return response.json()
    except Exception as e:
        st.error(f"Failed to post data: {e}")
        return {}

# Sidebar
with st.sidebar:
    st.title("🔥 ncOS Journal")
    st.markdown("### Phoenix Edition v21.7")
    
    page = st.selectbox(
        "Navigation",
        ["Dashboard", "Trade Entry", "Journal", "Analysis", "Statistics"]
    )
    
    st.markdown("---")
    
    # Quick stats
    stats = fetch_data("stats")
    if stats:
        st.metric("Total Trades", stats.get("trades", {}).get("total", 0))
        st.metric("Win Rate", f"{stats.get('trades', {}).get('win_rate', 0):.1f}%")
        st.metric("Journal Entries", stats.get("journal_entries", 0))

# Main content
if page == "Dashboard":
    st.title("📊 Trading Dashboard")
    
    # Fetch recent data
    trades_data = fetch_data("trades")
    trades = trades_data.get("trades", [])
    
    if trades:
        # Convert to DataFrame
        df = pd.DataFrame(trades)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(trades))
        
        with col2:
            winning_trades = sum(1 for t in trades if t.get("exit_price", 0) > t.get("entry_price", 0))
            st.metric("Winning Trades", winning_trades)
        
        with col3:
            symbols = list(set(t.get("symbol", "") for t in trades))
            st.metric("Symbols Traded", len(symbols))
        
        with col4:
            today_trades = sum(1 for t in trades if t.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d")))
            st.metric("Today's Trades", today_trades)
        
        # Recent trades table
        st.subheader("Recent Trades")
        recent_trades = df.tail(10)[["timestamp", "symbol", "side", "entry_price", "exit_price", "notes"]]
        st.dataframe(recent_trades)
        
        # Pattern analysis
        if any(t.get("patterns") for t in trades):
            st.subheader("Pattern Performance")
            pattern_data = {}
            for trade in trades:
                for pattern in trade.get("patterns", []):
                    if pattern not in pattern_data:
                        pattern_data[pattern] = {"total": 0, "wins": 0}
                    pattern_data[pattern]["total"] += 1
                    if trade.get("exit_price", 0) > trade.get("entry_price", 0):
                        pattern_data[pattern]["wins"] += 1
            
            pattern_df = pd.DataFrame([
                {
                    "Pattern": p,
                    "Total": d["total"],
                    "Wins": d["wins"],
                    "Win Rate": (d["wins"] / d["total"] * 100) if d["total"] > 0 else 0
                }
                for p, d in pattern_data.items()
            ])
            
            fig = px.bar(pattern_df, x="Pattern", y="Win Rate", title="Pattern Win Rates")
            st.plotly_chart(fig)
    else:
        st.info("No trades recorded yet. Start by entering a trade!")

elif page == "Trade Entry":
    st.title("📝 Trade Entry")
    
    with st.form("trade_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", value="XAUUSD")
            side = st.selectbox("Side", ["long", "short"])
            entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
            exit_price = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)
        
        with col2:
            quantity = st.number_input("Quantity", min_value=0.01, step=0.01, value=0.01)
            stop_loss = st.number_input("Stop Loss", min_value=0.0, step=0.01)
            take_profit = st.number_input("Take Profit", min_value=0.0, step=0.01)
            session_id = st.text_input("Session ID", value=f"session_{datetime.now().strftime('%Y%m%d')}")
        
        patterns = st.multiselect(
            "Patterns",
            ["Wyckoff Spring", "Order Block", "FVG", "Liquidity Sweep", "Break of Structure"]
        )
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Submit Trade")
        
        if submitted:
            trade_data = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "exit_price": exit_price if exit_price > 0 else None,
                "quantity": quantity,
                "stop_loss": stop_loss if stop_loss > 0 else None,
                "take_profit": take_profit if take_profit > 0 else None,
                "patterns": patterns,
                "notes": notes,
                "session_id": session_id
            }
            
            result = post_data("trades", trade_data)
            if result.get("id"):
                st.success(f"Trade recorded! ID: {result['id']}")
            else:
                st.error("Failed to record trade")

elif page == "Journal":
    st.title("📔 Trading Journal")
    
    tab1, tab2 = st.tabs(["View Entries", "New Entry"])
    
    with tab1:
        entries_data = fetch_data("journal")
        entries = entries_data.get("entries", [])
        
        if entries:
            for entry in entries:
                with st.expander(f"{entry.get('title')} - {entry.get('timestamp', '')[:10]}"):
                    st.markdown(entry.get("content", ""))
                    if entry.get("tags"):
                        st.write("Tags:", ", ".join(entry["tags"]))
        else:
            st.info("No journal entries yet.")
    
    with tab2:
        with st.form("journal_form"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=300)
            category = st.selectbox(
                "Category",
                ["general", "trade_review", "market_analysis", "psychology", "strategy"]
            )
            tags = st.text_input("Tags (comma-separated)")
            
            submitted = st.form_submit_button("Save Entry")
            
            if submitted and title and content:
                journal_data = {
                    "title": title,
                    "content": content,
                    "category": category,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()]
                }
                
                result = post_data("journal", journal_data)
                if result.get("id"):
                    st.success("Journal entry saved!")
                    st.experimental_rerun()

elif page == "Analysis":
    st.title("🔍 Market Analysis")
    
    analyses_data = fetch_data("analysis")
    analyses = analyses_data.get("analyses", [])
    
    if analyses:
        # Group by symbol
        symbols = list(set(a.get("symbol", "") for a in analyses))
        selected_symbol = st.selectbox("Select Symbol", symbols)
        
        symbol_analyses = [a for a in analyses if a.get("symbol") == selected_symbol]
        
        for analysis in symbol_analyses:
            with st.expander(f"{analysis.get('analysis_type')} - {analysis.get('timestamp', '')[:16]}"):
                st.json(analysis.get("content", {}))
    else:
        st.info("No analyses recorded yet.")

elif page == "Statistics":
    st.title("📈 Trading Statistics")
    
    stats = fetch_data("stats")
    
    if stats:
        # Overall metrics
        st.subheader("Overall Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Trades", stats.get("trades", {}).get("total", 0))
        with col2:
            st.metric("Win Rate", f"{stats.get('trades', {}).get('win_rate', 0):.1f}%")
        with col3:
            st.metric("Total Analyses", stats.get("analyses", 0))
        
        # Pattern statistics
        if stats.get("patterns"):
            st.subheader("Pattern Usage")
            pattern_df = pd.DataFrame([
                {"Pattern": p, "Count": c}
                for p, c in stats["patterns"].items()
            ])
            
            fig = px.pie(pattern_df, values="Count", names="Pattern", title="Pattern Distribution")
            st.plotly_chart(fig)
        
        # Symbol distribution
        if stats.get("symbols"):
            st.subheader("Symbols Traded")
            st.write(", ".join(stats["symbols"]))

# Footer
st.markdown("---")
st.markdown("🔥 ncOS Journal - Phoenix Edition v21.7")
'''

with open('dashboard/app.py', 'w') as f:
    f.write(dashboard_app)
print("✅ Created: dashboard/app.py")

# Create requirements file
requirements = '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
streamlit==1.29.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
python-dateutil==2.8.2
'''

with open('requirements_journal.txt', 'w') as f:
    f.write(requirements)
print("✅ Created: requirements_journal.txt")

# Create launch script
launch_script = '''#!/bin/bash

# ncOS Journal Launch Script - Phoenix Edition

echo "🚀 Starting ncOS Journal System..."

# Create necessary directories
mkdir -p data logs

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements_journal.txt

# Start API server
echo "Starting API server on port 8001..."
cd api
python main.py > ../logs/api.log 2>&1 &
API_PID=$!
cd ..

# Wait for API to start
sleep 3

# Start Dashboard
echo "Starting Dashboard on port 8501..."
cd dashboard
streamlit run app.py --server.port 8501 > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
cd ..

echo ""
echo "✨ ncOS Journal System is running!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔌 API: http://localhost:8001"
echo "📝 API Docs: http://localhost:8001/docs"
echo ""
echo "Process IDs:"
echo "  API: $API_PID"
echo "  Dashboard: $DASHBOARD_PID"
'''

with open('launch_journal.sh', 'w') as f:
    f.write(launch_script)
os.chmod('launch_journal.sh', 0o755)
print("✅ Created: launch_journal.sh")

print("\n✅ All files created successfully!")
print("\nDirectory structure:")
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '', 1).count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        if not file.startswith('.'):
            print(f'{subindent}{file}')