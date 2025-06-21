"""
Enhanced Conflict Detector with ncOS Journal Integration
Identifies and logs potential conflicts between active trades and new setups
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests
from pydantic import BaseModel

from production.production_config import load_production_config

logger = logging.getLogger(__name__)

# Journal API endpoint
CONFIG = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))
JOURNAL_API = CONFIG.api.journal

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
