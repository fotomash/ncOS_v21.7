import os
import json

# Create the directory structure
os.makedirs('ncos_journal/api', exist_ok=True)
os.makedirs('ncos_journal/dashboard', exist_ok=True)
os.makedirs('ncos_journal/core', exist_ok=True)
os.makedirs('ncos_journal/data/journals', exist_ok=True)
os.makedirs('ncos_journal/data/analysis', exist_ok=True)

# Create __init__.py files
for dir in ['ncos_journal', 'ncos_journal/api', 'ncos_journal/dashboard', 'ncos_journal/core']:
    with open(f'{dir}/__init__.py', 'w') as f:
        f.write('')

# Create the API main.py
api_main_content = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from pathlib import Path

app = FastAPI(title="ncOS Journal API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
JOURNALS_DIR = DATA_DIR / "journals"
ANALYSIS_DIR = DATA_DIR / "analysis"

# Ensure directories exist
JOURNALS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic models
class TradeEntry(BaseModel):
    symbol: str
    side: str  # buy/sell
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    timestamp: datetime
    notes: Optional[str] = None
    patterns: Optional[List[str]] = None
    pnl: Optional[float] = None

class JournalEntry(BaseModel):
    title: str
    content: str
    category: str = "general"
    tags: Optional[List[str]] = None
    timestamp: datetime = None

class AnalysisEntry(BaseModel):
    symbol: str
    analysis_type: str
    content: dict
    timestamp: datetime = None

@app.get("/")
def read_root():
    return {
        "message": "ncOS Journal API v2.0",
        "endpoints": {
            "trades": "/trades",
            "journal": "/journal",
            "analysis": "/analysis",
            "stats": "/stats"
        }
    }

@app.post("/trades")
def create_trade(trade: TradeEntry):
    """Log a new trade"""
    trade_dict = trade.dict()
    trade_dict['timestamp'] = trade_dict['timestamp'].isoformat()
    
    # Save to JSONL file
    trades_file = JOURNALS_DIR / f"trades_{datetime.now().strftime('%Y%m')}.jsonl"
    with open(trades_file, 'a') as f:
        f.write(json.dumps(trade_dict) + '\\n')
    
    return {"message": "Trade logged successfully", "trade": trade_dict}

@app.get("/trades")
def get_trades(limit: int = 100):
    """Get recent trades"""
    trades = []
    
    # Read from all trade files
    for file in sorted(JOURNALS_DIR.glob("trades_*.jsonl"), reverse=True):
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    trades.append(json.loads(line))
                    if len(trades) >= limit:
                        return trades
    
    return trades

@app.post("/journal")
def create_journal_entry(entry: JournalEntry):
    """Create a new journal entry"""
    if entry.timestamp is None:
        entry.timestamp = datetime.now()
    
    entry_dict = entry.dict()
    entry_dict['timestamp'] = entry_dict['timestamp'].isoformat()
    
    # Save to JSONL file
    journal_file = JOURNALS_DIR / f"journal_{datetime.now().strftime('%Y%m')}.jsonl"
    with open(journal_file, 'a') as f:
        f.write(json.dumps(entry_dict) + '\\n')
    
    return {"message": "Journal entry created", "entry": entry_dict}

@app.get("/journal")
def get_journal_entries(limit: int = 50, category: Optional[str] = None):
    """Get journal entries"""
    entries = []
    
    for file in sorted(JOURNALS_DIR.glob("journal_*.jsonl"), reverse=True):
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if category is None or entry.get('category') == category:
                        entries.append(entry)
                        if len(entries) >= limit:
                            return entries
    
    return entries

@app.post("/analysis")
def create_analysis(analysis: AnalysisEntry):
    """Log analysis results"""
    if analysis.timestamp is None:
        analysis.timestamp = datetime.now()
    
    analysis_dict = analysis.dict()
    analysis_dict['timestamp'] = analysis_dict['timestamp'].isoformat()
    
    # Save to JSONL file
    analysis_file = ANALYSIS_DIR / f"analysis_{analysis.symbol}_{datetime.now().strftime('%Y%m')}.jsonl"
    with open(analysis_file, 'a') as f:
        f.write(json.dumps(analysis_dict) + '\\n')
    
    return {"message": "Analysis logged", "analysis": analysis_dict}

@app.get("/stats")
def get_stats():
    """Get trading statistics"""
    trades = get_trades(limit=1000)
    
    if not trades:
        return {"message": "No trades found"}
    
    total_trades = len(trades)
    profitable_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    
    return {
        "total_trades": total_trades,
        "profitable_trades": profitable_trades,
        "win_rate": profitable_trades / total_trades if total_trades > 0 else 0,
        "total_pnl": total_pnl,
        "average_pnl": total_pnl / total_trades if total_trades > 0 else 0
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
'''

with open('ncos_journal/api/main.py', 'w') as f:
    f.write(api_main_content)

print("Created API main.py")

# Create the Dashboard app.py
dashboard_content = '''import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ncOS Journal Dashboard",
    page_icon="📊",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Title
st.title("📊 ncOS Journal Dashboard v2.0")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Overview", "Trades", "Journal", "Analysis", "New Entry"])

# Helper functions
def fetch_trades():
    try:
        response = requests.get(f"{API_URL}/trades")
        return response.json()
    except:
        return []

def fetch_journal():
    try:
        response = requests.get(f"{API_URL}/journal")
        return response.json()
    except:
        return []

def fetch_stats():
    try:
        response = requests.get(f"{API_URL}/stats")
        return response.json()
    except:
        return {}

# Main content
if page == "Overview":
    st.header("Trading Overview")
    
    # Stats
    stats = fetch_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", stats.get("total_trades", 0))
    
    with col2:
        st.metric("Win Rate", f"{stats.get('win_rate', 0)*100:.1f}%")
    
    with col3:
        st.metric("Total P&L", f"${stats.get('total_pnl', 0):,.2f}")
    
    with col4:
        st.metric("Avg P&L", f"${stats.get('average_pnl', 0):,.2f}")
    
    # Recent trades chart
    trades = fetch_trades()
    if trades:
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # P&L over time
        st.subheader("P&L Over Time")
        if 'pnl' in df.columns:
            df_sorted = df.sort_values('timestamp')
            df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_sorted['timestamp'],
                y=df_sorted['cumulative_pnl'],
                mode='lines+markers',
                name='Cumulative P&L'
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Trades":
    st.header("Trade History")
    
    trades = fetch_trades()
    if trades:
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            symbol_filter = st.selectbox(
                "Filter by Symbol",
                ["All"] + list(df['symbol'].unique())
            )
        
        with col2:
            side_filter = st.selectbox(
                "Filter by Side",
                ["All", "buy", "sell"]
            )
        
        # Apply filters
        if symbol_filter != "All":
            df = df[df['symbol'] == symbol_filter]
        if side_filter != "All":
            df = df[df['side'] == side_filter]
        
        # Display table
        st.dataframe(
            df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No trades found")

elif page == "Journal":
    st.header("Journal Entries")
    
    entries = fetch_journal()
    if entries:
        for entry in entries[:20]:  # Show last 20 entries
            with st.expander(f"{entry['title']} - {entry['timestamp']}"):
                st.write(entry['content'])
                if entry.get('tags'):
                    st.write(f"Tags: {', '.join(entry['tags'])}")
    else:
        st.info("No journal entries found")

elif page == "Analysis":
    st.header("Market Analysis")
    
    # Placeholder for analysis display
    st.info("Analysis visualization coming soon...")

elif page == "New Entry":
    st.header("Create New Entry")
    
    entry_type = st.radio("Entry Type", ["Trade", "Journal", "Analysis"])
    
    if entry_type == "Trade":
        with st.form("trade_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Symbol", "XAUUSD")
                side = st.selectbox("Side", ["buy", "sell"])
                entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
                quantity = st.number_input("Quantity", min_value=0.01, step=0.01)
            
            with col2:
                exit_price = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)
                pnl = st.number_input("P&L (optional)", step=0.01)
                patterns = st.text_input("Patterns (comma-separated)")
            
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Log Trade"):
                trade_data = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat(),
                    "notes": notes
                }
                
                if exit_price > 0:
                    trade_data["exit_price"] = exit_price
                if pnl != 0:
                    trade_data["pnl"] = pnl
                if patterns:
                    trade_data["patterns"] = [p.strip() for p in patterns.split(",")]
                
                try:
                    response = requests.post(f"{API_URL}/trades", json=trade_data)
                    if response.status_code == 200:
                        st.success("Trade logged successfully!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif entry_type == "Journal":
        with st.form("journal_form"):
            title = st.text_input("Title")
            category = st.selectbox("Category", ["general", "strategy", "psychology", "review"])
            content = st.text_area("Content", height=200)
            tags = st.text_input("Tags (comma-separated)")
            
            if st.form_submit_button("Create Entry"):
                entry_data = {
                    "title": title,
                    "content": content,
                    "category": category
                }
                
                if tags:
                    entry_data["tags"] = [t.strip() for t in tags.split(",")]
                
                try:
                    response = requests.post(f"{API_URL}/journal", json=entry_data)
                    if response.status_code == 200:
                        st.success("Journal entry created!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("ncOS Journal v2.0")
st.sidebar.markdown("Focus on journaling, not voice")
'''

with open('ncos_journal/dashboard/app.py', 'w') as f:
    f.write(dashboard_content)

print("Created Dashboard app.py")

# Create the requirements.txt if it doesn't exist
requirements_content = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.2
pandas==2.1.3
pyarrow==14.0.1
pydantic==2.5.0
plotly==5.18.0
requests==2.31.0
'''

with open('ncos_journal/requirements.txt', 'w') as f:
    f.write(requirements_content)

print("Created requirements.txt")

# Create a simple config file
config_content = {
    "journal": {
        "data_dir": "data",
        "formats": ["csv", "jsonl", "parquet"],
        "default_format": "jsonl"
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8000
    },
    "dashboard": {
        "port": 8501
    }
}

with open('ncos_journal/config.json', 'w') as f:
    json.dump(config_content, f, indent=2)

print("Created config.json")

print("\nDirectory structure created successfully!")
print("\nNow you can run: ./ncos_journal/launch.sh")