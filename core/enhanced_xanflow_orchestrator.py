"""
Enhanced XANFLOW Orchestrator with Journal Integration
Manages ISPTS pipeline execution with comprehensive logging
"""

import json
import logging
import os
import queue
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests

from production.production_config import load_production_config

logger = logging.getLogger(__name__)

# Journal API endpoint
CONFIG = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))
JOURNAL_API = CONFIG.api.journal

@dataclass
class PipelineStage:
    """Represents a stage in the ISPTS pipeline"""
    name: str
    agent: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class EnhancedXanflowOrchestrator:
    """Enhanced orchestrator with journal integration"""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pipeline_queue = queue.Queue()
        self.results = {}
        self.journal_enabled = True

    def _log_to_journal(self, entry_type: str, data: Dict[str, Any]):
        """Log pipeline events to journal"""
        if not self.journal_enabled:
            return

        try:
            if entry_type == "pipeline":
                # Log as journal entry
                journal_data = {
                    "title": f"Pipeline Execution: {data.get('pipeline_id')}",
                    "content": json.dumps(data, indent=2),
                    "category": "pipeline_execution",
                    "tags": ["pipeline", data.get("status", "unknown")]
                }
                requests.post(f"{JOURNAL_API}/journal", json=journal_data)

            elif entry_type == "stage":
                # Log as analysis entry
                analysis_data = {
                    "symbol": data.get("symbol", "SYSTEM"),
                    "analysis_type": "pipeline_stage",
                    "content": data
                }
                requests.post(f"{JOURNAL_API}/analysis", json=analysis_data)

        except Exception as e:
            logger.error(f"Failed to log to journal: {e}")

    def execute_ispts_pipeline(
        self,
        symbol: str,
        timeframe: str,
        session_id: str,
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the ISPTS pipeline with comprehensive logging
        """
        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize pipeline context
        pipeline_context = {
            "pipeline_id": pipeline_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "session_id": session_id,
            "initial_context": initial_context,
            "start_time": datetime.now().isoformat(),
            "stages": []
        }

        # Define pipeline stages
        stages = [
            PipelineStage(name="market_analysis", agent="MarketAnalyzer", input_data=initial_context),
            PipelineStage(name="pattern_detection", agent="PatternDetector", input_data={}),
            PipelineStage(name="risk_assessment", agent="RiskManager", input_data={}),
            PipelineStage(name="trade_decision", agent="DecisionMaker", input_data={}),
            PipelineStage(name="execution_planning", agent="ExecutionPlanner", input_data={})
        ]

        # Execute stages
        for i, stage in enumerate(stages):
            try:
                stage.start_time = datetime.now()
                stage.status = "running"

                # Pass output from previous stage as input
                if i > 0 and stages[i-1].output_data:
                    stage.input_data.update(stages[i-1].output_data)

                # Execute stage
                stage.output_data = self._execute_stage(stage, pipeline_context)

                stage.status = "completed"
                stage.end_time = datetime.now()

                # Log stage completion
                stage_data = {
                    "pipeline_id": pipeline_id,
                    "stage": stage.name,
                    "status": stage.status,
                    "duration": (stage.end_time - stage.start_time).total_seconds(),
                    "symbol": symbol,
                    "session_id": session_id
                }
                self._log_to_journal("stage", stage_data)

            except Exception as e:
                stage.status = "failed"
                stage.error = str(e)
                stage.end_time = datetime.now()
                logger.error(f"Stage {stage.name} failed: {e}")

                # Log stage failure
                stage_data = {
                    "pipeline_id": pipeline_id,
                    "stage": stage.name,
                    "status": "failed",
                    "error": str(e),
                    "symbol": symbol,
                    "session_id": session_id
                }
                self._log_to_journal("stage", stage_data)
                break

        # Compile pipeline results
        pipeline_context["stages"] = [
            {
                "name": s.name,
                "status": s.status,
                "duration": (s.end_time - s.start_time).total_seconds() if s.end_time and s.start_time else None,
                "error": s.error
            }
            for s in stages
        ]
        pipeline_context["end_time"] = datetime.now().isoformat()
        pipeline_context["status"] = "completed" if all(s.status == "completed" for s in stages) else "failed"

        # Generate final output
        final_output = {
            "pipeline_id": pipeline_id,
            "status": pipeline_context["status"],
            "symbol": symbol,
            "session_id": session_id,
            "trade_decision": stages[-1].output_data if stages[-1].status == "completed" else None,
            "execution_context": self._build_execution_context(stages)
        }

        # Log complete pipeline execution
        self._log_to_journal("pipeline", pipeline_context)

        # If trade decision was made, log it separately
        if final_output["trade_decision"] and final_output["trade_decision"].get("execute_trade"):
            self._log_trade_decision(final_output["trade_decision"], session_id, pipeline_id)

        return final_output

    def _execute_stage(self, stage: PipelineStage, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pipeline stage"""
        # Placeholder for actual agent execution
        # In production, this would call the appropriate agent

        if stage.name == "market_analysis":
            return {
                "market_bias": "bullish",
                "key_levels": [2650, 2655, 2660],
                "volatility": "medium"
            }
        elif stage.name == "pattern_detection":
            return {
                "patterns": ["Wyckoff Spring", "Order Block"],
                "confidence": 0.85
            }
        elif stage.name == "risk_assessment":
            return {
                "risk_score": 0.3,
                "position_size": 0.02,
                "stop_loss": 2645,
                "take_profit": 2665
            }
        elif stage.name == "trade_decision":
            return {
                "execute_trade": True,
                "direction": "long",
                "entry_price": 2650.50,
                "reasoning": "Strong bullish setup with favorable risk/reward"
            }
        elif stage.name == "execution_planning":
            return {
                "execution_type": "limit",
                "entry_zones": [2650.00, 2650.50],
                "scaling_plan": "single_entry"
            }

        return {}

    def _build_execution_context(self, stages: List[PipelineStage]) -> Dict[str, Any]:
        """Build comprehensive execution context from all stages"""
        context = {}

        for stage in stages:
            if stage.output_data:
                context[stage.name] = stage.output_data

        return context

    def _log_trade_decision(self, decision: Dict[str, Any], session_id: str, pipeline_id: str):
        """Log trade decision as a trade entry"""
        trade_data = {
            "symbol": decision.get("symbol", "UNKNOWN"),
            "side": decision.get("direction", "unknown"),
            "entry_price": decision.get("entry_price", 0),
            "quantity": decision.get("position_size", 0.01),
            "timestamp": datetime.now().isoformat(),
            "notes": decision.get("reasoning", ""),
            "patterns": decision.get("patterns", []),
            "session_id": session_id,
            "trace_id": pipeline_id
        }

        try:
            requests.post(f"{JOURNAL_API}/trades", json=trade_data)
        except Exception as e:
            logger.error(f"Failed to log trade decision: {e}")

# Usage example
if __name__ == "__main__":
    orchestrator = EnhancedXanflowOrchestrator()

    result = orchestrator.execute_ispts_pipeline(
        symbol="XAUUSD",
        timeframe="M15",
        session_id="session_20250621_1000",
        initial_context={
            "market_state": "trending",
            "session_type": "london"
        }
    )

    print(f"Pipeline Result: {json.dumps(result, indent=2)}")
