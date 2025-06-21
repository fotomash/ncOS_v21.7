"""
Enhanced Trade Narrative LLM with Journal Integration
Generates comprehensive trade narratives and insights
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List

import requests

from production.production_config import load_production_config

logger = logging.getLogger(__name__)

# Journal API endpoint
CONFIG = load_production_config(os.environ.get("NCOS_CONFIG_PATH"))
JOURNAL_API = CONFIG.api.journal


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

        return "\n".join(pattern_desc)

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

        return "\n".join(factors) if factors else "Standard confluence present"

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

        return "\n".join(analysis) if analysis else "No pattern data available"

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
