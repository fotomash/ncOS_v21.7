#!/usr/bin/env python3
"""
Enhanced Master Orchestrator for ncOS v21.7
Incorporates patterns from llm_orchestrator.py and agent_profile_schemas.py
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

# Import agent profile schema
try:
    from schemas.agent_profile_schemas import AgentProfileSchema
    from schemas.module_configs import (
        BaseModuleConfig, DataIngestionConfig, ContextAnalyzerConfig,
        LiquidityEngineConfig, StructureValidatorConfig, RiskManagerConfig,
        ConfluenceStackerConfig, ExecutorConfig, JournalerConfig
    )
except ImportError:
    from pydantic import BaseModel, Field
    class BaseModuleConfig(BaseModel):
        enabled: bool = True
        class Config:
            extra = "allow"

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """
    Master orchestrator that manages the entire ncOS pipeline execution.
    Based on patterns from your llm_orchestrator and agent profile schemas.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/ncos_config.yaml"
        self.config = self._load_config()
        self.agents = {}
        self.state = {"initialized": False}
        self.journal_path = Path("logs/trade_journal.jsonl")

        # Initialize logging
        self._setup_logging()

        # Load agent profiles
        self._load_agent_profiles()

        logger.info(f"MasterOrchestrator initialized with {len(self.agents)} agents")

    def _load_config(self) -> dict:
        """Load main configuration"""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Default configuration if no config file exists"""
        return {
            "system": {
                "name": "ncOS",
                "version": "21.7",
                "log_level": "INFO"
            },
            "orchestration": {
                "max_parallel_agents": 5,
                "timeout": 300,
                "retry_count": 3
            },
            "voice": {
                "enabled": True,
                "wake_word": "ncos"
            }
        }

    def _setup_logging(self):
        """Configure logging based on config"""
        log_level = self.config.get("system", {}).get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _load_agent_profiles(self):
        """Load all agent profiles from config directory"""
        agent_dir = Path("config/agents")
        if agent_dir.exists():
            for agent_file in agent_dir.glob("*.yaml"):
                try:
                    with open(agent_file, 'r') as f:
                        profile_data = yaml.safe_load(f)

                    # Validate with schema if available
                    if 'AgentProfileSchema' in globals():
                        profile = AgentProfileSchema(**profile_data)
                        self.agents[profile.profile_name] = profile.dict()
                    else:
                        self.agents[profile_data.get('profile_name', agent_file.stem)] = profile_data

                    logger.info(f"Loaded agent profile: {agent_file.stem}")
                except Exception as e:
                    logger.error(f"Failed to load agent {agent_file}: {e}")

    def route_command(self, prompt: str) -> Any:
        """
        Route natural language commands to appropriate handlers.
        Based on llm_orchestrator.py pattern.
        """
        prompt_lower = prompt.lower()

        # Voice journal commands
        if "mark" in prompt_lower or "tag" in prompt_lower:
            return self._handle_voice_tag(prompt)

        # ZBAR analysis commands
        if "scan" in prompt_lower and any(symbol in prompt_lower for symbol in ["xauusd", "gold", "btc", "eur"]):
            symbol = self._extract_symbol(prompt_lower)
            return self._run_zbar_analysis(symbol)

        # Show analysis results
        if "show" in prompt_lower and ("entry" in prompt_lower or "analysis" in prompt_lower):
            return self._show_latest_analysis(prompt_lower)

        # Session commands
        if "session" in prompt_lower:
            if "start" in prompt_lower:
                return self._start_session()
            elif "end" in prompt_lower or "stop" in prompt_lower:
                return self._end_session()
            elif "recap" in prompt_lower:
                return self._session_recap()

        return f"[ORCHESTRATOR] Command not recognized: {prompt}"

    def _handle_voice_tag(self, prompt: str) -> str:
        """Handle voice tagging for journal"""
        # Extract key information
        parts = prompt.split()
        symbol = "XAUUSD"  # default
        bias = "neutral"
        timeframe = "H1"

        for i, word in enumerate(parts):
            if word.upper() in ["XAUUSD", "GOLD", "BTCUSD", "EURUSD"]:
                symbol = word.upper()
            elif word.lower() in ["bullish", "bearish", "neutral"]:
                bias = word.lower()
            elif word.upper() in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
                timeframe = word.upper()

        # Log to journal
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "voice_tag",
            "symbol": symbol,
            "bias": bias,
            "timeframe": timeframe,
            "raw_prompt": prompt,
            "session_id": self.state.get("session_id", "default")
        }

        self._append_to_journal(entry)

        return f"✓ Tagged: {symbol} {bias} on {timeframe}"

    def _run_zbar_analysis(self, symbol: str) -> dict:
        """Run ZBAR analysis for symbol"""
        logger.info(f"Running ZBAR analysis for {symbol}")

        # This would integrate with your actual ZBAR module
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "ZBAR",
            "result": {
                "bias": "bullish",
                "entry": 2.0,
                "stop_loss": 1.98,
                "take_profit": 2.04,
                "confidence": 0.75
            }
        }

        # Log to journal
        self._append_to_journal(analysis)

        return analysis

    def _append_to_journal(self, entry: dict):
        """Append entry to JSONL journal"""
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _extract_symbol(self, text: str) -> str:
        """Extract trading symbol from text"""
        symbol_map = {
            "gold": "XAUUSD",
            "xauusd": "XAUUSD",
            "btc": "BTCUSD",
            "bitcoin": "BTCUSD",
            "eur": "EURUSD",
            "euro": "EURUSD"
        }

        for key, symbol in symbol_map.items():
            if key in text:
                return symbol
        return "XAUUSD"  # default

    def _show_latest_analysis(self, prompt: str) -> str:
        """Show latest analysis from journal"""
        if not self.journal_path.exists():
            return "No analysis found in journal"

        # Read last few entries
        with open(self.journal_path, 'r') as f:
            lines = f.readlines()

        # Find latest analysis
        for line in reversed(lines[-10:]):
            entry = json.loads(line)
            if entry.get("analysis_type") == "ZBAR":
                return f"Latest analysis for {entry['symbol']}:\n{json.dumps(entry['result'], indent=2)}"

        return "No recent ZBAR analysis found"

    def _start_session(self) -> str:
        """Start a new trading session"""
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.state["session_id"] = session_id
        self.state["session_start"] = datetime.utcnow().isoformat()

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "session_start",
            "session_id": session_id
        }
        self._append_to_journal(entry)

        return f"✓ Started session: {session_id}"

    def _end_session(self) -> str:
        """End current trading session"""
        if "session_id" not in self.state:
            return "No active session"

        session_id = self.state["session_id"]
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "session_end",
            "session_id": session_id,
            "duration": self._calculate_session_duration()
        }
        self._append_to_journal(entry)

        # Clear session state
        self.state.pop("session_id", None)
        self.state.pop("session_start", None)

        return f"✓ Ended session: {session_id}"

    def _session_recap(self) -> dict:
        """Generate session recap"""
        if not self.journal_path.exists():
            return {"error": "No journal found"}

        current_session = self.state.get("session_id", "default")

        with open(self.journal_path, 'r') as f:
            entries = [json.loads(line) for line in f]

        # Filter by session
        session_entries = [e for e in entries if e.get("session_id") == current_session]

        # Analyze entries
        trades = [e for e in session_entries if e.get("analysis_type") == "ZBAR"]
        voice_tags = [e for e in session_entries if e.get("type") == "voice_tag"]

        recap = {
            "session_id": current_session,
            "total_entries": len(session_entries),
            "trades_analyzed": len(trades),
            "voice_tags": len(voice_tags),
            "symbols": list(set(e.get("symbol") for e in session_entries if e.get("symbol")))
        }

        return recap

    def _calculate_session_duration(self) -> str:
        """Calculate session duration"""
        if "session_start" not in self.state:
            return "unknown"

        start = datetime.fromisoformat(self.state["session_start"])
        duration = datetime.utcnow() - start
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    async def run_pipeline(self, symbol: str, variant: str = "default") -> dict:
        """
        Run the full trading pipeline for a symbol.
        This integrates all modules in the execution sequence.
        """
        logger.info(f"Running pipeline for {symbol} with variant {variant}")

        # This would execute your actual pipeline
        # For now, returning a placeholder
        return {
            "status": "completed",
            "symbol": symbol,
            "variant": variant,
            "timestamp": datetime.utcnow().isoformat()
        }

# Compatibility shim for imports
enhanced_master_orchestrator = MasterOrchestrator

if __name__ == "__main__":
    orchestrator = MasterOrchestrator()
    print("MasterOrchestrator initialized successfully")
