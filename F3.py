# Create refactored versions that integrate with the journaling system

# 1. Enhanced Conflict Detector with Journal Integration
enhanced_conflict_detector = '''"""
Enhanced Conflict Detector with ncOS Journal Integration
Identifies and logs potential conflicts between active trades and new setups
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import json
import requests

logger = logging.getLogger(__name__)

# Journal API endpoint
JOURNAL_API = "http://localhost:8000"

class ConflictDetectionConfig(BaseModel):
    """Configuration for conflict detection"""
    same_direction_threshold: float = 0.8
    opposite_direction_threshold: float = 0.6
    correlation_window: int = 20
    log_to_journal: bool = True

class ActiveTradeContext(BaseModel):
    """Context for currently active trade"""
    symbol: str
    direction: str  # 'long' or 'short'
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    session_id: str
    trace_id: str

class MaturingSetupContext(BaseModel):
    """Context for newly maturing trade setup"""
    symbol: str
    direction: str
    proposed_entry: float
    proposed_stop: float
    proposed_target: float
    confidence_score: float
    patterns: List[str]
    session_id: str

class ConflictReport(BaseModel):
    """Detailed conflict analysis report"""
    conflict_detected: bool
    conflict_type: Optional[str] = None  # 'same_direction', 'opposite_direction', 'correlated_asset'
    severity: Optional[str] = None  # 'low', 'medium', 'high'
    recommendation: str
    risk_assessment: Dict[str, Any]
    timestamp: datetime = None

class EnhancedConflictDetector:
    """Enhanced conflict detector with journal integration"""
    
    def __init__(self, config: ConflictDetectionConfig = None):
        self.config = config or ConflictDetectionConfig()
        self.journal_enabled = self.config.log_to_journal
        
    def _log_to_journal(self, entry_type: str, data: Dict[str, Any]):
        """Log conflict analysis to journal"""
        if not self.journal_enabled:
            return
            
        try:
            if entry_type == "conflict":
                # Log as analysis entry
                analysis_data = {
                    "symbol": data.get("symbol", "MULTI"),
                    "analysis_type": "conflict_detection",
                    "content": data
                }
                requests.post(f"{JOURNAL_API}/analysis", json=analysis_data)
                
            elif entry_type == "decision":
                # Log as journal entry
                journal_data = {
                    "title": f"Conflict Detection: {data.get('decision')}",
                    "content": json.dumps(data, indent=2),
                    "category": "risk_management",
                    "tags": ["conflict", "risk", data.get("severity", "unknown")]
                }
                requests.post(f"{JOURNAL_API}/journal", json=journal_data)
                
        except Exception as e:
            logger.error(f"Failed to log to journal: {e}")
    
    def check_for_conflict(
        self,
        active_trade: ActiveTradeContext,
        maturing_setup: MaturingSetupContext
    ) -> ConflictReport:
        """
        Check for conflicts between active trade and new setup
        Logs all decisions to journal for review
        """
        
        conflict_data = {
            "active_trade": active_trade.dict(),
            "maturing_setup": maturing_setup.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Same asset conflict
        if active_trade.symbol == maturing_setup.symbol:
            if active_trade.direction == maturing_setup.direction:
                # Same direction - potential pyramid
                report = ConflictReport(
                    conflict_detected=True,
                    conflict_type="same_direction",
                    severity="low",
                    recommendation="Consider pyramiding if risk allows",
                    risk_assessment={
                        "current_exposure": self._calculate_exposure(active_trade),
                        "additional_risk": self._calculate_risk(maturing_setup),
                        "correlation": 1.0
                    },
                    timestamp=datetime.now()
                )
            else:
                # Opposite direction - high conflict
                report = ConflictReport(
                    conflict_detected=True,
                    conflict_type="opposite_direction",
                    severity="high",
                    recommendation="Avoid - conflicting with active position",
                    risk_assessment={
                        "conflict_reason": "Opposite direction on same asset",
                        "potential_hedge": False,
                        "recommended_action": "skip_setup"
                    },
                    timestamp=datetime.now()
                )
        else:
            # Different assets - check correlation
            correlation = self._check_correlation(active_trade.symbol, maturing_setup.symbol)
            
            if abs(correlation) > self.config.same_direction_threshold:
                report = ConflictReport(
                    conflict_detected=True,
                    conflict_type="correlated_asset",
                    severity="medium",
                    recommendation=f"High correlation ({correlation:.2f}) - consider total exposure",
                    risk_assessment={
                        "correlation": correlation,
                        "combined_risk": self._calculate_combined_risk(active_trade, maturing_setup)
                    },
                    timestamp=datetime.now()
                )
            else:
                report = ConflictReport(
                    conflict_detected=False,
                    recommendation="No significant conflict detected",
                    risk_assessment={
                        "correlation": correlation,
                        "diversification_benefit": True
                    },
                    timestamp=datetime.now()
                )
        
        # Log the complete analysis
        conflict_data["report"] = report.dict()
        self._log_to_journal("conflict", conflict_data)
        
        # Log the decision
        decision_data = {
            "decision": report.recommendation,
            "severity": report.severity,
            "conflict_type": report.conflict_type,
            "symbols": [active_trade.symbol, maturing_setup.symbol],
            "session_id": maturing_setup.session_id
        }
        self._log_to_journal("decision", decision_data)
        
        return report
    
    def _calculate_exposure(self, trade: ActiveTradeContext) -> float:
        """Calculate current trade exposure"""
        # Simplified calculation
        return abs(trade.current_price - trade.entry_price) / trade.entry_price
    
    def _calculate_risk(self, setup: MaturingSetupContext) -> float:
        """Calculate risk for new setup"""
        return abs(setup.proposed_entry - setup.proposed_stop) / setup.proposed_entry
    
    def _check_correlation(self, symbol1: str, symbol2: str) -> float:
        """Check correlation between two symbols"""
        # Placeholder - in production, this would query historical data
        correlations = {
            ("XAUUSD", "XAGUSD"): 0.85,
            ("EURUSD", "GBPUSD"): 0.75,
            ("USDJPY", "USDCHF"): -0.80,
        }
        
        pair = tuple(sorted([symbol1, symbol2]))
        return correlations.get(pair, 0.0)
    
    def _calculate_combined_risk(
        self,
        active: ActiveTradeContext,
        maturing: MaturingSetupContext
    ) -> Dict[str, float]:
        """Calculate combined risk metrics"""
        active_risk = self._calculate_risk(
            MaturingSetupContext(
                symbol=active.symbol,
                direction=active.direction,
                proposed_entry=active.entry_price,
                proposed_stop=active.stop_loss,
                proposed_target=active.take_profit,
                confidence_score=1.0,
                patterns=[],
                session_id=active.session_id
            )
        )
        
        new_risk = self._calculate_risk(maturing)
        
        return {
            "active_risk": active_risk,
            "new_risk": new_risk,
            "total_risk": active_risk + new_risk,
            "risk_concentration": max(active_risk, new_risk) / (active_risk + new_risk)
        }

# Usage example
if __name__ == "__main__":
    detector = EnhancedConflictDetector()
    
    # Example active trade
    active = ActiveTradeContext(
        symbol="XAUUSD",
        direction="long",
        entry_price=2650.50,
        current_price=2655.00,
        stop_loss=2645.00,
        take_profit=2665.00,
        entry_time=datetime.now(),
        session_id="session_20250621_1000",
        trace_id="trace_001"
    )
    
    # Example maturing setup
    maturing = MaturingSetupContext(
        symbol="XAGUSD",
        direction="long",
        proposed_entry=31.50,
        proposed_stop=31.00,
        proposed_target=32.50,
        confidence_score=0.85,
        patterns=["Wyckoff Spring", "Order Block"],
        session_id="session_20250621_1000"
    )
    
    # Check for conflicts
    report = detector.check_for_conflict(active, maturing)
    print(f"Conflict Report: {report.dict()}")
'''

with open('enhanced_conflict_detector.py', 'w') as f:
    f.write(enhanced_conflict_detector)

print("Created: enhanced_conflict_detector.py")

# 2. Enhanced XANFLOW Orchestrator with Journal Integration
enhanced_orchestrator = '''"""
Enhanced XANFLOW Orchestrator with Journal Integration
Manages ISPTS pipeline execution with comprehensive logging
"""

import logging
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Journal API endpoint
JOURNAL_API = "http://localhost:8000"

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
'''

with open('enhanced_xanflow_orchestrator.py', 'w') as f:
    f.write(enhanced_orchestrator)

print("Created: enhanced_xanflow_orchestrator.py")

# 3. Enhanced Trade Narrative LLM with Journal Integration
enhanced_narrative = '''"""
Enhanced Trade Narrative LLM with Journal Integration
Generates comprehensive trade narratives and insights
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)

# Journal API endpoint
JOURNAL_API = "http://localhost:8000"

class EnhancedTradeNarrativeLLM:
    """Enhanced narrative generator with journal integration"""
    
    def __init__(self):
        self.journal_enabled = True
        self.narrative_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load narrative templates"""
        return {
            "trade_setup": """
### Trade Setup Analysis - {symbol}
**Session**: {session_id}
**Time**: {timestamp}

#### Market Context
{market_context}

#### Pattern Recognition
{patterns_analysis}

#### Entry Rationale
{entry_reasoning}

#### Risk Management
- Entry: {entry_price}
- Stop Loss: {stop_loss} ({stop_pips} pips)
- Take Profit: {take_profit} ({tp_pips} pips)
- Risk/Reward: {risk_reward}

#### Confluence Factors
{confluence_factors}
""",
            "trade_review": """
### Trade Review - {symbol}
**Session**: {session_id}
**Duration**: {duration}
**Result**: {result}

#### Execution Analysis
{execution_analysis}

#### What Worked
{positive_aspects}

#### Areas for Improvement
{improvement_areas}

#### Lessons Learned
{lessons}

#### Cognitive State
{cognitive_assessment}
""",
            "session_summary": """
### Session Summary - {session_id}
**Date**: {date}
**Total Trades**: {total_trades}
**Win Rate**: {win_rate}%
**P&L**: {total_pnl}

#### Performance Highlights
{performance_highlights}

#### Pattern Success Rates
{pattern_analysis}

#### Key Decisions
{key_decisions}

#### Tomorrow's Preparation
{next_session_prep}
"""
        }
    
    def generate_trade_narrative(
        self,
        trade_context: Dict[str, Any],
        narrative_type: str = "trade_setup"
    ) -> str:
        """Generate comprehensive trade narrative"""
        
        # Select appropriate template
        template = self.narrative_templates.get(narrative_type, self.narrative_templates["trade_setup"])
        
        # Prepare narrative data based on type
        if narrative_type == "trade_setup":
            narrative_data = self._prepare_setup_narrative(trade_context)
        elif narrative_type == "trade_review":
            narrative_data = self._prepare_review_narrative(trade_context)
        elif narrative_type == "session_summary":
            narrative_data = self._prepare_session_narrative(trade_context)
        else:
            narrative_data = trade_context
        
        # Generate narrative
        narrative = template.format(**narrative_data)
        
        # Log to journal
        self._log_narrative_to_journal(narrative, narrative_type, trade_context)
        
        return narrative
    
    def _prepare_setup_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for trade setup narrative"""
        return {
            "symbol": context.get("symbol", "N/A"),
            "session_id": context.get("session_id", "N/A"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_context": self._analyze_market_context(context),
            "patterns_analysis": self._analyze_patterns(context.get("patterns", [])),
            "entry_reasoning": self._generate_entry_reasoning(context),
            "entry_price": context.get("entry_price", 0),
            "stop_loss": context.get("stop_loss", 0),
            "stop_pips": abs(context.get("entry_price", 0) - context.get("stop_loss", 0)) * 10000,
            "take_profit": context.get("take_profit", 0),
            "tp_pips": abs(context.get("take_profit", 0) - context.get("entry_price", 0)) * 10000,
            "risk_reward": self._calculate_risk_reward(context),
            "confluence_factors": self._analyze_confluence(context)
        }
    
    def _prepare_review_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for trade review narrative"""
        return {
            "symbol": context.get("symbol", "N/A"),
            "session_id": context.get("session_id", "N/A"),
            "duration": self._calculate_duration(context),
            "result": "WIN" if context.get("pnl", 0) > 0 else "LOSS",
            "execution_analysis": self._analyze_execution(context),
            "positive_aspects": self._identify_positives(context),
            "improvement_areas": self._identify_improvements(context),
            "lessons": self._extract_lessons(context),
            "cognitive_assessment": self._assess_cognitive_state(context)
        }
    
    def _prepare_session_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for session summary narrative"""
        trades = context.get("trades", [])
        wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
        
        return {
            "session_id": context.get("session_id", "N/A"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_trades": len(trades),
            "win_rate": (wins / len(trades) * 100) if trades else 0,
            "total_pnl": sum(t.get("pnl", 0) for t in trades),
            "performance_highlights": self._generate_highlights(trades),
            "pattern_analysis": self._analyze_pattern_performance(trades),
            "key_decisions": self._identify_key_decisions(trades),
            "next_session_prep": self._prepare_next_session(context)
        }
    
    def _analyze_market_context(self, context: Dict[str, Any]) -> str:
        """Analyze and describe market context"""
        bias = context.get("market_bias", "neutral")
        volatility = context.get("volatility", "medium")
        session = context.get("session_type", "unknown")
        
        return f"""
The market is showing a {bias} bias during the {session} session with {volatility} volatility.
Key support and resistance levels have been identified, with price action respecting these zones.
Volume profile indicates {context.get('volume_profile', 'normal')} participation.
"""
    
    def _analyze_patterns(self, patterns: List[str]) -> str:
        """Analyze detected patterns"""
        if not patterns:
            return "No specific patterns identified."
        
        pattern_desc = []
        for pattern in patterns:
            if "Wyckoff" in pattern:
                pattern_desc.append(f"- **{pattern}**: Indicating potential accumulation/distribution")
            elif "Order Block" in pattern:
                pattern_desc.append(f"- **{pattern}**: Strong institutional interest zone")
            elif "FVG" in pattern:
                pattern_desc.append(f"- **{pattern}**: Imbalance likely to be filled")
            else:
                pattern_desc.append(f"- **{pattern}**: Technical setup confirmed")
        
        return "\\n".join(pattern_desc)
    
    def _generate_entry_reasoning(self, context: Dict[str, Any]) -> str:
        """Generate entry reasoning"""
        reasons = []
        
        if context.get("patterns"):
            reasons.append(f"Multiple patterns confirmed: {', '.join(context['patterns'])}")
        
        if context.get("confluence_score", 0) > 0.7:
            reasons.append("High confluence score indicates strong setup")
        
        if context.get("risk_reward_ratio", 0) > 2:
            reasons.append("Favorable risk/reward ratio")
        
        return ". ".join(reasons) if reasons else "Standard entry criteria met."
    
    def _calculate_risk_reward(self, context: Dict[str, Any]) -> float:
        """Calculate risk/reward ratio"""
        entry = context.get("entry_price", 0)
        stop = context.get("stop_loss", 0)
        target = context.get("take_profit", 0)
        
        if entry and stop and target:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            return round(reward / risk, 2) if risk > 0 else 0
        return 0
    
    def _analyze_confluence(self, context: Dict[str, Any]) -> str:
        """Analyze confluence factors"""
        factors = []
        
        if context.get("technical_confluence"):
            factors.append("✓ Technical indicators aligned")
        
        if context.get("pattern_confluence"):
            factors.append("✓ Multiple pattern confirmation")
        
        if context.get("timeframe_confluence"):
            factors.append("✓ Multi-timeframe alignment")
        
        if context.get("volume_confluence"):
            factors.append("✓ Volume supports direction")
        
        return "\\n".join(factors) if factors else "Standard confluence present"
    
    def _log_narrative_to_journal(
        self,
        narrative: str,
        narrative_type: str,
        context: Dict[str, Any]
    ):
        """Log narrative to journal"""
        if not self.journal_enabled:
            return
        
        try:
            journal_data = {
                "title": f"{narrative_type.replace('_', ' ').title()} - {context.get('symbol', 'N/A')}",
                "content": narrative,
                "category": "narrative",
                "tags": [narrative_type, context.get("symbol", ""), context.get("session_id", "")]
            }
            
            requests.post(f"{JOURNAL_API}/journal", json=journal_data)
            
        except Exception as e:
            logger.error(f"Failed to log narrative: {e}")
    
    # Additional helper methods
    def _calculate_duration(self, context: Dict[str, Any]) -> str:
        """Calculate trade duration"""
        # Implementation depends on your data structure
        return context.get("duration", "N/A")
    
    def _analyze_execution(self, context: Dict[str, Any]) -> str:
        """Analyze trade execution quality"""
        return "Entry was executed as planned with minimal slippage."
    
    def _identify_positives(self, context: Dict[str, Any]) -> str:
        """Identify positive aspects of the trade"""
        return "Pattern recognition was accurate. Risk management rules followed."
    
    def _identify_improvements(self, context: Dict[str, Any]) -> str:
        """Identify areas for improvement"""
        return "Consider tighter entry criteria for similar setups."
    
    def _extract_lessons(self, context: Dict[str, Any]) -> str:
        """Extract lessons learned"""
        return "Patience in waiting for confluence pays off."
    
    def _assess_cognitive_state(self, context: Dict[str, Any]) -> str:
        """Assess cognitive state during trade"""
        return "Maintained discipline throughout the trade execution."
    
    def _generate_highlights(self, trades: List[Dict[str, Any]]) -> str:
        """Generate performance highlights"""
        return "Consistent execution across all trades."
    
    def _analyze_pattern_performance(self, trades: List[Dict[str, Any]]) -> str:
        """Analyze pattern performance"""
        pattern_stats = {}
        for trade in trades:
            for pattern in trade.get("patterns", []):
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {"total": 0, "wins": 0}
                pattern_stats[pattern]["total"] += 1
                if trade.get("pnl", 0) > 0:
                    pattern_stats[pattern]["wins"] += 1
        
        analysis = []
        for pattern, stats in pattern_stats.items():
            win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            analysis.append(f"- {pattern}: {win_rate:.1f}% success rate ({stats['total']} trades)")
        
        return "\\n".join(analysis) if analysis else "No pattern data available"
    
    def _identify_key_decisions(self, trades: List[Dict[str, Any]]) -> str:
        """Identify key trading decisions"""
        return "Key decisions were made based on confluence and risk management."
    
    def _prepare_next_session(self, context: Dict[str, Any]) -> str:
        """Prepare for next trading session"""
        return "Review today's trades and prepare watchlist for tomorrow."

# Usage example
if __name__ == "__main__":
    narrator = EnhancedTradeNarrativeLLM()
    
    # Generate trade setup narrative
    trade_context = {
        "symbol": "XAUUSD",
        "session_id": "session_20250621_1000",
        "entry_price": 2650.50,
        "stop_loss": 2645.00,
        "take_profit": 2665.00,
        "patterns": ["Wyckoff Spring", "Order Block", "Bullish FVG"],
        "market_bias": "bullish",
        "confluence_score": 0.85,
        "risk_reward_ratio": 2.73
    }
    
    narrative = narrator.generate_trade_narrative(trade_context, "trade_setup")
    print(narrative)
'''

with open('enhanced_trade_narrative_llm.py', 'w') as f:
    f.write(enhanced_narrative)

print("Created: enhanced_trade_narrative_llm.py")

# Create integration guide
integration_guide = '''# Integration Guide for Enhanced Components

## Overview
The enhanced components add comprehensive journaling capabilities to your existing XANFLOW/ZANFLOW system.

## 1. Enhanced Conflict Detector

### Key Features:
- Automatic journal logging of all conflict analyses
- Detailed risk assessment documentation
- Session-based conflict tracking
- Correlation analysis between assets

### Integration:
```python
from enhanced_conflict_detector import EnhancedConflictDetector, ActiveTradeContext, MaturingSetupContext

# Initialize detector
detector = EnhancedConflictDetector()

# Check conflicts and auto-log to journal
report = detector.check_for_conflict(active_trade, maturing_setup)

'''