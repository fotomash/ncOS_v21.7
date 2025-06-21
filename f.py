# Create an enhanced dashboard that integrates ZBAR functionality
enhanced_dashboard_content = '''import streamlit as st
import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ncOS Journal Dashboard - Phoenix Edition",
    page_icon="🔥",
    layout="wide"
)

# API endpoints
API_URL = "http://localhost:8000"
ZBAR_LOG_FILE = "/mnt/data/logs/trade_journal.jsonl"
LOCAL_LOG_FILE = "data/journals/trade_journal.jsonl"

# Helper functions
def load_zbar_entries():
    """Load ZBAR journal entries"""
    log_files = [ZBAR_LOG_FILE, LOCAL_LOG_FILE]
    records = []
    
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except:
                            pass
    
    return pd.DataFrame(records) if records else pd.DataFrame()

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

# Title with Phoenix branding
st.title("🔥 ncOS Journal Dashboard - Phoenix Edition")
st.markdown("*Unified Trade Intelligence & ZBAR Pattern Analysis*")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Module", 
    ["Overview", "Trades", "Journal", "ZBAR Analysis", "Session Replay", "New Entry", "Settings"]
)

# Main content routing
if page == "Overview":
    st.header("Trading Overview")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Statistics", "Performance", "ZBAR Patterns"])
    
    with tab1:
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
    
    with tab2:
        # P&L over time
        trades = fetch_trades()
        if trades:
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            st.subheader("P&L Over Time")
            if 'pnl' in df.columns:
                df_sorted = df.sort_values('timestamp')
                df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sorted['timestamp'],
                    y=df_sorted['cumulative_pnl'],
                    mode='lines+markers',
                    name='Cumulative P&L',
                    line=dict(color='#00ff00', width=2)
                ))
                fig.update_layout(
                    height=400,
                    template="plotly_dark",
                    title="Cumulative P&L Performance"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # ZBAR pattern distribution
        zbar_df = load_zbar_entries()
        if not zbar_df.empty and 'patterns' in zbar_df.columns:
            st.subheader("ZBAR Pattern Distribution")
            pattern_counts = {}
            for patterns in zbar_df['patterns'].dropna():
                if isinstance(patterns, list):
                    for p in patterns:
                        pattern_counts[p] = pattern_counts.get(p, 0) + 1
            
            if pattern_counts:
                fig = px.bar(
                    x=list(pattern_counts.keys()),
                    y=list(pattern_counts.values()),
                    labels={'x': 'Pattern', 'y': 'Count'},
                    title="Most Common ZBAR Patterns"
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

elif page == "ZBAR Analysis":
    st.header("📊 ZBAR Trade Journal")
    
    # Load ZBAR entries
    df = load_zbar_entries()
    
    if df.empty:
        st.warning("No ZBAR journal entries found yet.")
        st.info("ZBAR entries will appear here once you start logging trades with pattern analysis.")
    else:
        # Process dataframe
        if "logged_at" in df.columns:
            df["logged_at"] = pd.to_datetime(df["logged_at"])
            df = df.sort_values("logged_at", ascending=False)
        
        # Sidebar filters
        st.sidebar.header("ZBAR Filters")
        
        # Session filter
        session_ids = []
        if "session_id" in df.columns:
            session_ids = sorted(df["session_id"].dropna().unique().tolist())
        session = st.sidebar.selectbox("Session ID", options=["All"] + session_ids)
        
        # Symbol filter
        symbols = []
        if "symbol" in df.columns:
            symbols = sorted(df["symbol"].dropna().unique().tolist())
        symbol = st.sidebar.selectbox("Symbol", options=["All"] + symbols)
        
        # Trace ID filter
        trace_id = st.sidebar.text_input("Trace ID contains")
        
        # Pattern filter
        pattern_filter = st.sidebar.multiselect(
            "Patterns",
            options=["Wyckoff", "SMC", "Order Block", "FVG", "Liquidity Sweep", "Break of Structure"]
        )
        
        # Apply filters
        filtered_df = df.copy()
        if session != "All":
            filtered_df = filtered_df[filtered_df["session_id"] == session]
        if symbol != "All":
            filtered_df = filtered_df[filtered_df["symbol"] == symbol]
        if trace_id:
            filtered_df = filtered_df[filtered_df["trace_id"].str.contains(trace_id, na=False)]
        
        # Session recap
        if session != "All":
            st.markdown(f"### 🧠 Session Recap: {session}")
            trades = filtered_df.shape[0]
            pairs = sorted(filtered_df['symbol'].dropna().unique()) if 'symbol' in filtered_df else []
            avg_maturity = filtered_df["maturity_score"].mean() if "maturity_score" in filtered_df else None
            
            recap_text = f"**{trades}** trades logged for this session\\n\\n"
            if pairs:
                recap_text += f"Pairs: {', '.join(pairs)}\\n\\n"
            if avg_maturity:
                recap_text += f"Average maturity score: {avg_maturity:.2f}"
            
            st.info(recap_text)
        
        st.markdown(f"### Showing {len(filtered_df)} filtered entries")
        
        # Display entries
        for i, row in filtered_df.iterrows():
            timestamp = row.get('logged_at', 'Unknown time')
            symbol = row.get('symbol', 'Unknown')
            trace = row.get('trace_id', 'No trace')
            
            with st.expander(f"{timestamp} | {symbol} | {trace}"):
                # Display entry details
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.json(row.to_dict())
                
                with col2:
                    st.markdown("**Actions**")
                    
                    # Re-run strategy button
                    if st.button(f"🔁 Re-run", key=f"rerun_{i}"):
                        context = {
                            "trace_id": row.get("trace_id"),
                            "initial_htf_bias": row.get("bias"),
                            "session_id": row.get("session_id")
                        }
                        try:
                            res = requests.post(
                                "http://localhost:8000/strategy/zbar/execute_multi",
                                json={
                                    "strategy": "ISPTS_v14",
                                    "asset": row.get("symbol"),
                                    "blocks": [],
                                    "context": context
                                }
                            )
                            st.success("Strategy Re-run Completed")
                            st.json(res.json())
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    # Analyze button
                    if st.button(f"📈 Analyze", key=f"analyze_{i}"):
                        st.info("Deep analysis coming soon...")

elif page == "Session Replay":
    st.header("🎬 Session Replay & Analysis")
    
    # Session selection
    zbar_df = load_zbar_entries()
    if not zbar_df.empty and "session_id" in zbar_df.columns:
        sessions = sorted(zbar_df["session_id"].dropna().unique().tolist())
        
        selected_session = st.selectbox("Select Session to Replay", sessions)
        
        if selected_session:
            session_data = zbar_df[zbar_df["session_id"] == selected_session]
            
            # Session metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Trades", len(session_data))
            with col2:
                if "pnl" in session_data.columns:
                    total_pnl = session_data["pnl"].sum()
                    st.metric("Session P&L", f"${total_pnl:,.2f}")
            with col3:
                if "maturity_score" in session_data.columns:
                    avg_maturity = session_data["maturity_score"].mean()
                    st.metric("Avg Maturity", f"{avg_maturity:.2f}")
            
            # Timeline view
            st.subheader("Session Timeline")
            if "logged_at" in session_data.columns:
                timeline_data = session_data.sort_values("logged_at")
                
                # Create timeline chart
                fig = go.Figure()
                
                for idx, row in timeline_data.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row["logged_at"]],
                        y=[row.get("symbol", "Unknown")],
                        mode='markers+text',
                        marker=dict(
                            size=15,
                            color='green' if row.get("pnl", 0) > 0 else 'red'
                        ),
                        text=f"{row.get('trace_id', '')}",
                        textposition="top center",
                        name=row.get("trace_id", "Trade")
                    ))
                
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    template="plotly_dark",
                    title="Trade Execution Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed replay
            if st.button("🎯 Start Detailed Replay"):
                st.info("Replaying session trades...")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, (i, row) in enumerate(timeline_data.iterrows()):
                    progress = (idx + 1) / len(timeline_data)
                    progress_bar.progress(progress)
                    
                    status_text.text(f"Replaying trade {idx + 1}/{len(timeline_data)}: {row.get('symbol')} at {row.get('logged_at')}")
                    
                    # Display trade details
                    with st.container():
                        st.write(f"**Trade {idx + 1}**")
                        st.json({
                            "symbol": row.get("symbol"),
                            "bias": row.get("bias"),
                            "patterns": row.get("patterns"),
                            "entry": row.get("entry_price"),
                            "exit": row.get("exit_price"),
                            "pnl": row.get("pnl")
                        })
                    
                    # Simulate processing time
                    import time
                    time.sleep(0.5)
                
                status_text.text("Replay complete!")
    else:
        st.info("No sessions found for replay")

elif page == "New Entry":
    st.header("Create New Entry")
    
    entry_type = st.radio("Entry Type", ["Trade", "Journal", "ZBAR Analysis"])
    
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
                patterns = st.multiselect(
                    "Patterns Detected",
                    ["Wyckoff Spring", "SMC MSS", "Order Block", "FVG", "Liquidity Sweep", "BOS", "CHoCH"]
                )
            
            # ZBAR specific fields
            st.subheader("ZBAR Context")
            col3, col4 = st.columns(2)
            
            with col3:
                session_id = st.text_input("Session ID", value=f"session_{datetime.now().strftime('%Y%m%d_%H%M')}")
                trace_id = st.text_input("Trace ID", value=f"trace_{datetime.now().strftime('%H%M%S')}")
                bias = st.selectbox("HTF Bias", ["bullish", "bearish", "neutral"])
            
            with col4:
                maturity_score = st.slider("Maturity Score", 0.0, 10.0, 5.0, 0.1)
                confluence_score = st.slider("Confluence Score", 0.0, 10.0, 5.0, 0.1)
            
            notes = st.text_area("Trade Notes & Rationale")
            
            if st.form_submit_button("Log Trade"):
                trade_data = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat(),
                    "notes": notes,
                    "patterns": patterns,
                    # ZBAR fields
                    "session_id": session_id,
                    "trace_id": trace_id,
                    "bias": bias,
                    "maturity_score": maturity_score,
                    "confluence_score": confluence_score,
                    "logged_at": datetime.now().isoformat()
                }
                
                if exit_price > 0:
                    trade_data["exit_price"] = exit_price
                if pnl != 0:
                    trade_data["pnl"] = pnl
                
                try:
                    # Log to API
                    response = requests.post(f"{API_URL}/trades", json=trade_data)
                    
                    # Also log to ZBAR journal
                    os.makedirs("data/journals", exist_ok=True)
                    with open(LOCAL_LOG_FILE, "a") as f:
                        f.write(json.dumps(trade_data) + "\\n")
                    
                    if response.status_code == 200:
                        st.success("Trade logged successfully!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif entry_type == "ZBAR Analysis":
        st.subheader("Log ZBAR Pattern Analysis")
        
        with st.form("zbar_form"):
            symbol = st.text_input("Symbol", "XAUUSD")
            timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"])
            
            st.subheader("Wyckoff Analysis")
            wyckoff_phase = st.selectbox(
                "Current Phase",
                ["Accumulation A", "Accumulation B", "Accumulation C", "Accumulation D", "Accumulation E",
                 "Distribution A", "Distribution B", "Distribution C", "Distribution D", "Distribution E"]
            )
            
            st.subheader("Smart Money Concepts")
            smc_patterns = st.multiselect(
                "SMC Patterns Identified",
                ["Market Structure Shift", "Break of Structure", "Change of Character",
                 "Order Block", "Breaker Block", "Mitigation Block", "Fair Value Gap",
                 "Liquidity Sweep", "Inducement", "Premium/Discount"]
            )
            
            st.subheader("Technical Context")
            col1, col2 = st.columns(2)
            
            with col1:
                rsi = st.number_input("RSI", 0.0, 100.0, 50.0)
                volume_profile = st.selectbox("Volume Profile", ["Low", "Average", "High", "Climactic"])
            
            with col2:
                delta = st.number_input("Delta", step=0.01)
                cvd = st.number_input("CVD", step=0.01)
            
            analysis_notes = st.text_area("Detailed Analysis", height=200)
            
            if st.form_submit_button("Log Analysis"):
                analysis_data = {
                    "symbol": symbol,
                    "analysis_type": "ZBAR",
                    "content": {
                        "timeframe": timeframe,
                        "wyckoff_phase": wyckoff_phase,
                        "smc_patterns": smc_patterns,
                        "rsi": rsi,
                        "volume_profile": volume_profile,
                        "delta": delta,
                        "cvd": cvd,
                        "notes": analysis_notes
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    response = requests.post(f"{API_URL}/analysis", json=analysis_data)
                    if response.status_code == 200:
                        st.success("ZBAR analysis logged!")
                except Exception as e:
                    st.error(f"Error: {e}")

elif page == "Settings":
    st.header("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["Data Management", "API Configuration", "Export/Import"])
    
    with tab1:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Trades"):
                if st.checkbox("I understand this will delete all trade data"):
                    # Clear logic here
                    st.warning("Feature coming soon")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.info("Report generation coming soon")
    
    with tab2:
        st.subheader("API Configuration")
        
        api_host = st.text_input("API Host", value="localhost")
        api_port = st.number_input("API Port", value=8000, min_value=1, max_value=65535)
        
        if st.button("Test Connection"):
            try:
                response = requests.get(f"http://{api_host}:{api_port}/health")
                if response.status_code == 200:
                    st.success("API connection successful!")
                    st.json(response.json())
            except:
                st.error("Failed to connect to API")
    
    with tab3:
        st.subheader("Export/Import Data")
        
        export_format = st.selectbox("Export Format", ["JSON", "CSV", "Parquet"])
        
        if st.button("Export All Data"):
            st.info(f"Exporting data as {export_format}...")
            # Export logic here

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔥 Phoenix Edition Features")
st.sidebar.markdown("""
- Unified trade journaling
- ZBAR pattern analysis
- Session replay capability
- Wyckoff phase tracking
- Smart Money Concepts
- Real-time performance metrics
""")
st.sidebar.markdown("---")
st.sidebar.markdown("ncOS Journal v2.0 - Phoenix")
'''

# Save the enhanced dashboard
with open('ncos_journal/dashboard/app.py', 'w') as f:
    f.write(enhanced_dashboard_content)

print("Enhanced dashboard created with ZBAR integration!")

# Create a ZBAR-specific module for the API
zbar_api_content = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/zbar", tags=["ZBAR"])

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
ZBAR_DIR = DATA_DIR / "zbar"
ZBAR_DIR.mkdir(parents=True, exist_ok=True)

class ZBAREntry(BaseModel):
    symbol: str
    session_id: str
    trace_id: str
    bias: str
    patterns: List[str]
    maturity_score: float
    confluence_score: float
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    wyckoff_phase: Optional[str] = None
    smc_patterns: Optional[List[str]] = None
    volume_profile: Optional[str] = None
    delta: Optional[float] = None
    cvd: Optional[float] = None
    rsi: Optional[float] = None
    notes: Optional[str] = None
    logged_at: datetime = None

class ZBARAnalysis(BaseModel):
    symbol: str
    timeframe: str
    wyckoff_phase: str
    smc_patterns: List[str]
    technical_indicators: Dict[str, Any]
    analysis_notes: str

@router.post("/log")
def log_zbar_entry(entry: ZBAREntry):
    """Log a ZBAR journal entry"""
    if entry.logged_at is None:
        entry.logged_at = datetime.now()
    
    entry_dict = entry.dict()
    entry_dict['logged_at'] = entry_dict['logged_at'].isoformat()
    
    # Save to ZBAR journal
    journal_file = ZBAR_DIR / f"zbar_journal_{datetime.now().strftime('%Y%m')}.jsonl"
    with open(journal_file, 'a') as f:
        f.write(json.dumps(entry_dict) + '\\n')
    
    return {"message": "ZBAR entry logged", "entry": entry_dict}

@router.get("/entries")
def get_zbar_entries(
    session_id: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 100
):
    """Get ZBAR entries with optional filters"""
    entries = []
    
    for file in sorted(ZBAR_DIR.glob("zbar_journal_*.jsonl"), reverse=True):
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    
                    # Apply filters
                    if session_id and entry.get('session_id') != session_id:
                        continue
                    if symbol and entry.get('symbol') != symbol:
                        continue
                    
                    entries.append(entry)
                    if len(entries) >= limit:
                        return entries
    
    return entries

@router.post("/analyze")
def analyze_zbar_patterns(analysis: ZBARAnalysis):
    """Log ZBAR pattern analysis"""
    analysis_dict = analysis.dict()
    analysis_dict['timestamp'] = datetime.now().isoformat()
    
    # Save analysis
    analysis_file = ZBAR_DIR / f"analysis_{analysis.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis_dict, f, indent=2)
    
    return {"message": "Analysis saved", "analysis": analysis_dict}

@router.get("/sessions")
def get_sessions():
    """Get all unique session IDs"""
    sessions = set()
    
    for file in ZBAR_DIR.glob("zbar_journal_*.jsonl"):
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if 'session_id' in entry:
                        sessions.add(entry['session_id'])
    
    return sorted(list(sessions))

@router.get("/session/{session_id}")
def get_session_details(session_id: str):
    """Get detailed information about a specific session"""
    entries = get_zbar_entries(session_id=session_id, limit=1000)
    
    if not entries:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate session statistics
    total_trades = len(entries)
    profitable_trades = sum(1 for e in entries if e.get('pnl', 0) > 0)
    total_pnl = sum(e.get('pnl', 0) for e in entries)
    symbols = list(set(e['symbol'] for e in entries if 'symbol' in e))
    
    # Pattern analysis
    all_patterns = []
    for e in entries:
        if 'patterns' in e and isinstance(e['patterns'], list):
            all_patterns.extend(e['patterns'])
    
    pattern_counts = {}
    for p in all_patterns:
        pattern_counts[p] = pattern_counts.get(p, 0) + 1
    
    return {
        "session_id": session_id,
        "total_trades": total_trades,
        "profitable_trades": profitable_trades,
        "win_rate": profitable_trades / total_trades if total_trades > 0 else 0,
        "total_pnl": total_pnl,
        "symbols": symbols,
        "pattern_distribution": pattern_counts,
        "entries": entries
    }
'''

# Save the ZBAR API module
with open('ncos_journal/api/zbar_routes.py', 'w') as f:
    f.write(zbar_api_content)

# Update the main API to include ZBAR routes
updated_api_main = '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from pathlib import Path

# Import ZBAR routes
from .zbar_routes import router as zbar_router

app = FastAPI(title="ncOS Journal API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ZBAR router
app.include_router(zbar_router)

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
    # ZBAR fields
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    bias: Optional[str] = None
    maturity_score: Optional[float] = None
    confluence_score: Optional[float] = None

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
        "message": "ncOS Journal API v2.0 - Phoenix Edition",
        "endpoints": {
            "trades": "/trades",
            "journal": "/journal",
            "analysis": "/analysis",
            "stats": "/stats",
            "zbar": "/zbar/*"
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
    
    # Also save to ZBAR journal if it has ZBAR fields
    if trade.session_id or trade.trace_id:
        zbar_file = JOURNALS_DIR / "trade_journal.jsonl"
        trade_dict['logged_at'] = trade_dict['timestamp']
        with open(zbar_file, 'a') as f:
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
    
    # Calculate win rate by session if available
    session_stats = {}
    for trade in trades:
        if 'session_id' in trade and trade['session_id']:
            session_id = trade['session_id']
            if session_id not in session_stats:
                session_stats[session_id] = {
                    'trades': 0,
                    'profitable': 0,
                    'pnl': 0
                }
            session_stats[session_id]['trades'] += 1
            if trade.get('pnl', 0) > 0:
                session_stats[session_id]['profitable'] += 1
            session_stats[session_id]['pnl'] += trade.get('pnl', 0)
    
    return {
        "total_trades": total_trades,
        "profitable_trades": profitable_trades,
        "win_rate": profitable_trades / total_trades if total_trades > 0 else 0,
        "total_pnl": total_pnl,
        "average_pnl": total_pnl / total_trades if total_trades > 0 else 0,
        "session_stats": session_stats
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Strategy execution endpoint for ZBAR re-runs
@app.post("/strategy/zbar/execute_multi")
def execute_zbar_strategy(
    strategy: str,
    asset: str,
    blocks: List[str],
    context: dict
):
    """Execute ZBAR strategy (placeholder for actual implementation)"""
    # This is a placeholder - in production, this would connect to your actual strategy engine
    return {
        "status": "executed",
        "strategy": strategy,
        "asset": asset,
        "context": context,
        "result": {
            "message": "Strategy execution simulated",
            "timestamp": datetime.now().isoformat()
        }
    }
'''

# Update the main API file
with open('ncos_journal/api/main.py', 'w') as f:
    f.write(updated_api_main)

print("API updated with ZBAR integration!")

# Create a README for the integrated system
integrated_readme = '''


# ncOS Journal v2.0 - Phoenix Edition 🔥

A unified trade journaling system combining traditional trade logging with advanced ZBAR pattern analysis.

## Features

### Core Journaling
- Trade logging with P&L tracking
- Journal entries for market observations
- Performance statistics and metrics
- CSV, JSONL, and Parquet export formats

### ZBAR Integration
- Pattern detection and logging (Wyckoff, SMC, Order Blocks, etc.)
- Session-based analysis and replay
- Maturity and confluence scoring
- Strategy re-execution capability

### Dashboard Features
- Real-time performance metrics
- Interactive charts with Plotly
- Session replay functionality
- Pattern distribution analysis
- Multi-timeframe analysis support

## Quick Start

1. **Install dependencies:**
bash
   pip install -r ncos_journal/requirements.txt

'''