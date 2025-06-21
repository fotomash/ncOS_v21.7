
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="NCOS ZBAR Strategy API", version="5.0")

# --- Pydantic Models ---
class DataBlock(BaseModel):
    id: str
    timeframe: str
    columns: List[str]
    data: List[List[Any]]

class ExecutionContext(BaseModel):
    initial_htf_bias: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_profile: Optional[str] = "default"

class ZBARRequest(BaseModel):
    strategy: str
    asset: str
    blocks: List[DataBlock]
    context: Optional[ExecutionContext] = None

class EntrySignal(BaseModel):
    timestamp: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    rr: float
    killzone_match_name: Optional[str] = None

class PredictiveSnapshot(BaseModel):
    maturity_score: float
    grade: str
    conflict_signal: bool
    poi_quality: Optional[str] = None
    structure_alignment: Optional[str] = None

class ZBARResponse(BaseModel):
    status: str  # PASS or FAIL
    reason: Optional[str] = None
    entry_signal: Optional[EntrySignal] = None
    predictive_snapshot: Optional[PredictiveSnapshot] = None
    zbar_trace_id: str
    metadata: Optional[Dict[str, Any]] = None

# --- Journal Entry Model ---
class JournalEntry(BaseModel):
    timestamp: str
    trace_id: str
    session_id: str
    symbol: str
    strategy: str
    direction: Optional[str] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    maturity_score: Optional[float] = None
    status: str
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# --- Core ZBAR Logic (Placeholder) ---
class ZBARAgent:
    """Simulated ZBAR agent for demonstration"""

    def process_multi_timeframe(self, blocks: List[DataBlock], context: ExecutionContext) -> Dict[str, Any]:
        # Convert blocks to DataFrames
        dfs = {}
        for block in blocks:
            df = pd.DataFrame(block.data, columns=block.columns)
            dfs[block.timeframe] = df

        # Simulate ZBAR analysis
        # In production, this would call your actual zbar_agent.py

        # Example logic
        if context.initial_htf_bias == "bullish":
            return {
                "status": "PASS",
                "entry_signal": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "direction": "long",
                    "entry_price": 2360.1,
                    "stop_loss": 2357.3,
                    "take_profit": 2367.8,
                    "rr": 2.7,
                    "killzone_match_name": "London Open"
                },
                "predictive_snapshot": {
                    "maturity_score": 0.79,
                    "grade": "B",
                    "conflict_signal": False,
                    "poi_quality": "premium",
                    "structure_alignment": "aligned"
                }
            }
        else:
            return {
                "status": "FAIL",
                "reason": "No valid POI detected in premium zone"
            }

# --- Journal Manager ---
class JournalManager:
    def __init__(self, journal_path: Optional[str] = None):
        """Manage trade journal entries.

        Parameters
        ----------
        journal_path : str, optional
            Path to the journal file. If not provided, the value from the
            ``JOURNAL_PATH`` environment variable is used. If that is also not
            set, ``"trade_journal.jsonl"`` is used by default.
        """

        if journal_path is None:
            journal_path = os.environ.get("JOURNAL_PATH", "trade_journal.jsonl")
        self.journal_path = Path(journal_path)

    def log_entry(self, entry: JournalEntry):
        with open(self.journal_path, 'a') as f:
            f.write(entry.json() + '\n')

    def query_journal(self, filters: Dict[str, Any]) -> List[Dict]:
        entries = []
        if not self.journal_path.exists():
            return entries

        with open(self.journal_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                # Simple filter matching
                match = True
                for key, value in filters.items():
                    if key in entry and entry[key] != value:
                        match = False
                        break
                if match:
                    entries.append(entry)
        return entries

# Initialize components
zbar_agent = ZBARAgent()
# Journal path can be overridden via the JOURNAL_PATH environment variable
journal_manager = JournalManager()

# --- API Endpoints ---

@app.post("/strategy/zbar/execute_multi", response_model=ZBARResponse)
async def execute_zbar_multi(request: ZBARRequest):
    """Execute ZBAR strategy with multi-timeframe data blocks"""

    # Generate trace ID if not provided
    trace_id = request.context.trace_id if request.context and request.context.trace_id else f"zbar_{uuid.uuid4().hex[:8]}"

    try:
        # Process through ZBAR agent
        result = zbar_agent.process_multi_timeframe(
            request.blocks,
            request.context or ExecutionContext()
        )

        # Create response
        response = ZBARResponse(
            status=result["status"],
            reason=result.get("reason"),
            zbar_trace_id=trace_id
        )

        # Add entry signal if present
        if "entry_signal" in result:
            response.entry_signal = EntrySignal(**result["entry_signal"])

        # Add predictive snapshot if present
        if "predictive_snapshot" in result:
            response.predictive_snapshot = PredictiveSnapshot(**result["predictive_snapshot"])

        # Log to journal
        journal_entry = JournalEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            trace_id=trace_id,
            session_id=request.context.session_id if request.context else "default",
            symbol=request.asset,
            strategy=request.strategy,
            direction=response.entry_signal.direction if response.entry_signal else None,
            entry_price=response.entry_signal.entry_price if response.entry_signal else None,
            stop_loss=response.entry_signal.stop_loss if response.entry_signal else None,
            take_profit=response.entry_signal.take_profit if response.entry_signal else None,
            maturity_score=response.predictive_snapshot.maturity_score if response.predictive_snapshot else None,
            status=response.status,
            reason=response.reason
        )
        journal_manager.log_entry(journal_entry)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZBAR execution failed: {str(e)}")


@app.post("/journal/append")
async def append_journal(entry: JournalEntry):
    """Append a new entry to the trade journal"""
    try:
        journal_manager.log_entry(entry)
        return {"status": "success", "message": "Entry logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to append entry: {str(e)}")

@app.get("/journal/query")
async def query_journal(
    symbol: Optional[str] = None,
    strategy: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    limit: int = 100
):
    """Query the trade journal with filters"""

    filters = {}
    if symbol:
        filters["symbol"] = symbol
    if strategy:
        filters["strategy"] = strategy
    if session_id:
        filters["session_id"] = session_id
    if trace_id:
        filters["trace_id"] = trace_id

    entries = journal_manager.query_journal(filters)

    # Apply limit
    if len(entries) > limit:
        entries = entries[-limit:]

    return {
        "count": len(entries),
        "entries": entries
    }

@app.get("/journal/stats")
async def journal_stats():
    """Get journal statistics"""

    all_entries = journal_manager.query_journal({})

    if not all_entries:
        return {"message": "No journal entries found"}

    # Calculate stats
    total_trades = len(all_entries)
    passed_trades = len([e for e in all_entries if e.get("status") == "PASS"])
    failed_trades = len([e for e in all_entries if e.get("status") == "FAIL"])

    # Average maturity score for passed trades
    maturity_scores = [e.get("maturity_score", 0) for e in all_entries if e.get("status") == "PASS" and e.get("maturity_score")]
    avg_maturity = sum(maturity_scores) / len(maturity_scores) if maturity_scores else 0

    # Symbol distribution
    symbol_counts = {}
    for entry in all_entries:
        symbol = entry.get("symbol", "unknown")
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

    return {
        "total_trades": total_trades,
        "passed_trades": passed_trades,
        "failed_trades": failed_trades,
        "pass_rate": passed_trades / total_trades if total_trades > 0 else 0,
        "average_maturity_score": avg_maturity,
        "symbol_distribution": symbol_counts
    }

@app.get("/")
async def root():
    return {
        "service": "NCOS ZBAR Strategy API",
        "version": "5.0",
        "endpoints": [
            "/strategy/zbar/execute_multi",
            "/journal/append",
            "/journal/query",
            "/journal/stats"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting NCOS ZBAR Strategy API on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
