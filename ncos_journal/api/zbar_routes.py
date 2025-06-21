from fastapi import APIRouter, HTTPException
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
        f.write(json.dumps(entry_dict) + '\n')
    
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
