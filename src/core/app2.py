from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

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


# Save the ZBAR API module
with open('ncos_journal/api/zbar_routes.py', 'w') as f:
    f.write(zbar_api_content)

# Update the main API to include ZBAR routes
updated_api_main =

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import json
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
