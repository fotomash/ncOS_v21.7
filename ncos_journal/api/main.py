import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
        f.write(json.dumps(trade_dict) + '\n')
    
    # Also save to ZBAR journal if it has ZBAR fields
    if trade.session_id or trade.trace_id:
        zbar_file = JOURNALS_DIR / "trade_journal.jsonl"
        trade_dict['logged_at'] = trade_dict['timestamp']
        with open(zbar_file, 'a') as f:
            f.write(json.dumps(trade_dict) + '\n')
    
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
        f.write(json.dumps(entry_dict) + '\n')
    
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
        f.write(json.dumps(analysis_dict) + '\n')
    
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
