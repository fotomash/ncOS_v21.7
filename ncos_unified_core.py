#!/usr/bin/env python3
"""
ncOS Refactored Core System - Unified v21.7 (with Local Data Connector)

This script implements an intelligent data pipeline that connects to locally
enriched CSV files. It uses an "Agent Manifest" to determine the specific
data requirements (timeframe, number of bars) for each analysis agent.

Key Features:
- LocalDataConnector: Reads enriched CSV files from a specified directory.
- Agent Manifest: A configuration dictionary defining data needs for each agent.
- Intelligent Orchestrator: Uses the manifest to fetch the correct data slice.
- Session Memory Export: Saves session journals to CSV or JSONL.
"""

# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


# ==============================================================================
# 2. LOGGING SETUP
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ncOS_Core")


# ==============================================================================
# 3. UNIFIED PYDANTIC SCHEMAS
# ==============================================================================

class TradeJournalEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    session_id: str
    symbol: str
    strategy: str
    status: str
    reason: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class AgentManifest(BaseModel):
    """Defines the data requirements for an analysis agent."""
    description: str
    required_timeframe: str
    required_bars: int
    required_indicators: List[str]


# ==============================================================================
# 4. CORE AGENT & MANAGER IMPLEMENTATIONS
# ==============================================================================

class LocalDataConnector:
    """Agent to fetch data from a local directory of enriched CSV files."""
    def __init__(self, base_path: str = "./"):
        self.base_path = Path(base_path)
        logger.info(f"LocalDataConnector initialized. Watching directory: {self.base_path.resolve()}")

    def find_and_load(self, symbol: str, timeframe: str, bars_to_load: int, required_cols: List[str]) -> Optional[pd.DataFrame]:
        """Finds the correct enriched CSV, loads it, and returns the requested slice."""
        try:
            # Construct a pattern to find the relevant file
            pattern = f"{symbol}_{timeframe}_enriched.csv"
            found_files = list(self.base_path.glob(f"**/*{pattern}"))
            
            if not found_files:
                logger.error(f"No file found for pattern: *{pattern} in {self.base_path.resolve()}")
                return None
            
            file_path = found_files[0] # Use the first match
            logger.info(f"Found enriched data file: {file_path}")

            df = pd.read_csv(file_path)
            
            # Validate required indicator columns exist
            for col in required_cols:
                if col not in df.columns:
                    logger.warning(f"Required indicator '{col}' not found in {file_path}. Skipping.")
                    # In a production system, you might return None or raise an error
            
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            
            # Get the most recent `bars_to_load`
            df_sliced = df.tail(bars_to_load)
            logger.info(f"Loaded and sliced {len(df_sliced)} bars.")
            return df_sliced

        except Exception as e:
            logger.error(f"Error loading or processing data from file: {e}", exc_info=True)
            return None

class AnalysisAgent:
    """A generic agent to perform analysis on a provided DataFrame."""
    def __init__(self, agent_name: str):
        self.name = agent_name
        logger.info(f"{self.name} agent initialized.")

    def run_analysis(self, df: pd.DataFrame) -> Dict:
        """Runs a generic analysis and returns key stats."""
        logger.info(f"Agent '{self.name}' processing {len(df)} bars...")
        if df.empty:
            return {"status": "error", "message": "Input data is empty."}
        
        volatility = df['close'].pct_change().std()
        avg_volume = df['volume'].mean()

        return {
            "agent_name": self.name,
            "status": "success",
            "result": {
                "volatility": float(volatility),
                "average_volume": float(avg_volume),
                "message": f"Analysis complete on {len(df)} bars."
            }
        }

class JournalManager:
    def __init__(self, journal_path: str = "trade_journal.jsonl"):
        self.journal_path = Path(journal_path)
        self.entries = []
        if self.journal_path.exists():
            with self.journal_path.open('r') as f:
                for line in f:
                    self.entries.append(TradeJournalEntry(**json.loads(line)))
        logger.info(f"JournalManager initialized with {len(self.entries)} entries.")

    def log(self, entry: TradeJournalEntry):
        self.entries.append(entry)
        with self.journal_path.open('a') as f:
            f.write(entry.model_dump_json() + '\n')
            
    def export_session(self, session_id: str, format: str = 'jsonl') -> Optional[str]:
        session_entries = [e for e in self.entries if e.session_id == session_id]
        if not session_entries: return None
        
        export_dir = Path("session_exports"); export_dir.mkdir(exist_ok=True)
        file_path = export_dir / f"{session_id}.{format}"

        if format == 'jsonl':
            with file_path.open('w') as f:
                for entry in session_entries: f.write(entry.model_dump_json() + '\n')
        elif format == 'csv':
            pd.json_normalize([e.model_dump() for e in session_entries]).to_csv(file_path, index=False)
        else: return None
        return str(file_path)

# ==============================================================================
# 5. MASTER ORCHESTRATOR
# ==============================================================================

class MasterOrchestrator:
    def __init__(self, config: Dict):
        self.config = config
        self.journal = JournalManager()
        self.data_connector = LocalDataConnector()
        
        # AGENT MANIFESTS: Defines data requirements for each agent.
        self.agent_manifests: Dict[str, AgentManifest] = {
            "wyckoff_analyzer": AgentManifest(
                description="Performs Wyckoff phase analysis on higher timeframes.",
                required_timeframe="1H",
                required_bars=500,
                required_indicators=["volume", "vwap", "sma_50"]
            ),
            "smc_liquidity_sniper": AgentManifest(
                description="Looks for SMC liquidity sweeps on lower timeframes.",
                required_timeframe="15T",
                required_bars=200,
                required_indicators=["fractal_high", "fractal_low", "structure"]
            )
        }
        
        self.agents = {name: AnalysisAgent(name) for name in self.agent_manifests.keys()}
        self.active_session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Orchestrator ready. Active session: {self.active_session_id}")

    async def route_command(self, command: str) -> Dict:
        command = command.lower().strip()
        logger.info(f"Routing command: '{command}'")
        parts = command.split()
        
        self.journal.log(TradeJournalEntry(
            session_id=self.active_session_id, symbol="SYSTEM", strategy="manual_command",
            status="OBSERVATION", details={"command": command}
        ))

        if command.startswith("run agent"):
            # Format: "run agent <agent_name> on <symbol>"
            if len(parts) != 5: return {"error": "Invalid command format. Use: 'run agent <name> on <symbol>'"}
            agent_name = parts[2]
            symbol = parts[4].upper()
            return await self.handle_agent_run(agent_name, symbol)
            
        elif command.startswith("save session"):
            format = parts[-1] if parts[-1] in ['csv', 'jsonl'] else 'jsonl'
            return self.handle_session_save(format)
        else:
            return {"status": "unrecognized_command", "available_agents": list(self.agents.keys())}

    async def handle_agent_run(self, agent_name: str, symbol: str) -> Dict:
        """Handles loading data and running an agent based on its manifest."""
        if agent_name not in self.agent_manifests:
            return {"error": f"Agent '{agent_name}' not found."}
        
        manifest = self.agent_manifests[agent_name]
        logger.info(f"Executing '{agent_name}' with requirements: {manifest.required_bars} bars of {manifest.required_timeframe} data.")

        # Use the connector to get the data
        data_df = self.data_connector.find_and_load(
            symbol=symbol,
            timeframe=manifest.required_timeframe,
            bars_to_load=manifest.required_bars,
            required_cols=manifest.required_indicators
        )

        if data_df is None:
            return {"status": "error", "message": f"Could not load required data for {agent_name} on {symbol}."}
        
        # Get the agent and run its analysis
        agent = self.agents[agent_name]
        result = agent.run_analysis(data_df)
        
        # Log the successful analysis
        self.journal.log(TradeJournalEntry(
            session_id=self.active_session_id, symbol=symbol, strategy=agent_name,
            status="SUCCESS", reason="Analysis complete.", details=result
        ))
        
        return result

    def handle_session_save(self, format: str) -> Dict:
        """Handles saving the session journal."""
        file_path = self.journal.export_session(self.active_session_id, format)
        if file_path: return {"status": "success", "message": f"Session journal saved to {file_path}"}
        return {"status": "error", "message": "Could not save session."}

# ==============================================================================
# 6. FASTAPI APPLICATION SETUP
# ==============================================================================

app = FastAPI(title="ncOS Core with Data Connector", version="21.8")
orchestrator = MasterOrchestrator(config={})

@app.post("/command")
async def execute_command(command: str):
    return await orchestrator.route_command(command)

@app.get("/", tags=["Root"])
async def root(): return {"service": app.title, "version": app.version}

# ==============================================================================
# 7. MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    logger.info(f"Starting {app.title} Server on port 8008...")
    logger.info("Example command to try via API: 'run agent wyckoff_analyzer on BTCUSD'")
    uvicorn.run(app, host="0.0.0.0", port=8008)

