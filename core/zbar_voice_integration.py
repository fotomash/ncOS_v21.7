"""
ZBAR Agent Integration with Voice Commands
Extends your existing ZBAR pipeline with voice-triggered analysis
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
from engine import VectorEngine
# Import your existing modules
from zbar_agent import ZBARAgent
from zbar_logger import ZBARLogger

from voice_tag_parser import VoiceTagParser, VoiceTag


class VoiceEnabledZBARAgent(ZBARAgent):
    """ZBAR Agent with voice command integration"""

    def __init__(self, config_path: str = "zbar_config.yaml"):
        super().__init__(config_path)
        self.voice_parser = VoiceTagParser()
        self.voice_history = []

    def process_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """Process voice command and trigger appropriate ZBAR analysis"""

        # Parse voice input
        tag = self.voice_parser.parse(voice_input)
        self.voice_history.append(tag)

        # Log the voice command
        self.logger.log_event("voice_command", {
            "raw_input": voice_input,
            "parsed_tag": tag.__dict__,
            "timestamp": datetime.now().isoformat()
        })

        # Route based on action and confidence
        if tag.confidence < 0.4:
            return {
                "status": "error",
                "message": "Could not understand command clearly",
                "suggestions": self._get_voice_suggestions(tag)
            }

        # Execute based on parsed action
        if tag.action in ["mark", "log"]:
            return self._handle_mark_command(tag)
        elif tag.action in ["analyze", "scan"]:
            return self._handle_analyze_command(tag)
        elif tag.action in ["check", "monitor"]:
            return self._handle_check_command(tag)
        else:
            return self._handle_mark_command(tag)  # Default to marking

    def _handle_mark_command(self, tag: VoiceTag) -> Dict[str, Any]:
        """Handle mark/log commands - create journal entry"""

        # Create journal entry from voice tag
        journal_entry = {
            "timestamp": tag.timestamp,
            "symbol": tag.symbol or "XAUUSD",  # Default to gold
            "timeframe": tag.timeframe or "H4",  # Default to H4
            "bias": tag.bias,
            "session": tag.session,
            "maturity_score": tag.maturity_score,
            "notes": tag.notes,
            "source": "voice",
            "trace_id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        # Log to ZBAR journal
        self.logger.log_signal(
            signal_type="voice_mark",
            details=journal_entry,
            metadata={"voice_confidence": tag.confidence}
        )

        # Offer to run analysis
        response = {
            "status": "success",
            "action": "marked",
            "journal_entry": journal_entry,
            "message": f"Marked {journal_entry['symbol']} {journal_entry['timeframe']} as {journal_entry['bias']}"
        }

        if tag.symbol and tag.timeframe:
            response["follow_up"] = {
                "question": "Would you like to run ZBAR analysis now?",
                "action": "analyze",
                "params": {
                    "symbol": tag.symbol,
                    "timeframe": tag.timeframe,
                    "context": {"bias": tag.bias, "session": tag.session}
                }
            }

        return response

    def _handle_analyze_command(self, tag: VoiceTag) -> Dict[str, Any]:
        """Handle analyze/scan commands - run ZBAR analysis"""

        if not tag.symbol:
            return {
                "status": "error",
                "message": "Please specify a symbol to analyze",
                "example": "analyze XAUUSD on H4"
            }

        # Prepare analysis parameters
        symbol = tag.symbol
        timeframe = tag.timeframe or "H4"

        # Load data (assuming you have a data loader)
        try:
            # This would connect to your actual data pipeline
            data = self._load_market_data(symbol, timeframe)

            # Run ZBAR analysis with voice context
            analysis_result = self.analyze(
                data=data,
                context={
                    "initial_bias": tag.bias,
                    "session": tag.session,
                    "voice_triggered": True,
                    "voice_notes": tag.notes
                }
            )

            # Log the analysis
            self.logger.log_analysis(
                analysis_type="voice_triggered",
                result=analysis_result,
                metadata={
                    "voice_command": tag.raw_text,
                    "voice_confidence": tag.confidence
                }
            )

            return {
                "status": "success",
                "action": "analyzed",
                "symbol": symbol,
                "timeframe": timeframe,
                "analysis": analysis_result,
                "message": f"ZBAR analysis complete for {symbol} {timeframe}"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}",
                "symbol": symbol,
                "timeframe": timeframe
            }

    def _handle_check_command(self, tag: VoiceTag) -> Dict[str, Any]:
        """Handle check/monitor commands - query existing analysis"""

        # Build query filters from voice tag
        filters = {}
        if tag.symbol:
            filters["symbol"] = tag.symbol
        if tag.timeframe:
            filters["timeframe"] = tag.timeframe
        if tag.session:
            filters["session"] = tag.session
        if tag.bias:
            filters["bias"] = tag.bias

        # Query recent signals
        recent_signals = self.logger.query_signals(
            filters=filters,
            limit=10,
            include_voice=True
        )

        # Format response
        if recent_signals:
            summary = self._summarize_signals(recent_signals)
            return {
                "status": "success",
                "action": "checked",
                "count": len(recent_signals),
                "signals": recent_signals,
                "summary": summary,
                "message": f"Found {len(recent_signals)} matching signals"
            }
        else:
            return {
                "status": "success",
                "action": "checked",
                "count": 0,
                "message": "No matching signals found",
                "filters": filters
            }

    def _summarize_signals(self, signals: List[Dict]) -> Dict[str, Any]:
        """Summarize signals for voice response"""

        # Group by symbol and bias
        summary = {
            "total": len(signals),
            "by_symbol": {},
            "by_bias": {"bullish": 0, "bearish": 0, "neutral": 0},
            "avg_maturity": 0,
            "sessions": set()
        }

        maturity_scores = []

        for signal in signals:
            # Symbol counts
            symbol = signal.get("symbol", "unknown")
            summary["by_symbol"][symbol] = summary["by_symbol"].get(symbol, 0) + 1

            # Bias counts
            bias = signal.get("bias", "neutral")
            if bias in summary["by_bias"]:
                summary["by_bias"][bias] += 1

            # Maturity scores
            if signal.get("maturity_score"):
                maturity_scores.append(signal["maturity_score"])

            # Sessions
            if signal.get("session"):
                summary["sessions"].add(signal["session"])

        # Calculate averages
        if maturity_scores:
            summary["avg_maturity"] = sum(maturity_scores) / len(maturity_scores)

        summary["sessions"] = list(summary["sessions"])

        return summary

    def voice_to_zbar_pipeline(self, voice_input: str, auto_execute: bool = False) -> Dict[str, Any]:
        """Complete pipeline from voice to ZBAR analysis"""

        # Process voice command
        result = self.process_voice_command(voice_input)

        # Auto-execute analysis if requested and possible
        if auto_execute and result.get("follow_up") and result["follow_up"]["action"] == "analyze":
            # Extract parameters from follow-up
            params = result["follow_up"]["params"]

            # Create synthetic voice command for analysis
            analyze_command = f"analyze {params['symbol']} {params['timeframe']}"

            # Run analysis
            analysis_result = self.process_voice_command(analyze_command)

            # Combine results
            result["auto_analysis"] = analysis_result

        return result

    def _load_market_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Load market data for analysis - connects to your data pipeline"""
        # This is a placeholder - connect to your actual data loading
        # Could load from parquet, CSV, or live feed

        # Example: Load from your enriched parquet files
        file_path = f"data/{symbol}_{timeframe}_enriched.parquet"
        if Path(file_path).exists():
            return pd.read_parquet(file_path)
        else:
            # Fallback to generating sample data
            return self._generate_sample_data(symbol, timeframe)


# Example usage function
def demo_voice_zbar_integration():
    """Demonstrate voice-enabled ZBAR agent"""

    # Initialize voice-enabled agent
    agent = VoiceEnabledZBARAgent()

    # Example voice commands
    voice_commands = [
        "Mark gold bullish on H4 during London session",
        "Analyze XAUUSD 15 minute chart",
        "Check all bullish setups from today",
        "Scan for high maturity trades in New York session",
        "Log EURUSD potential reversal at resistance, maturity 85"
    ]

    print("=== Voice-Enabled ZBAR Agent Demo ===\n")

    for command in voice_commands:
        print(f"Voice: '{command}'")
        result = agent.voice_to_zbar_pipeline(command, auto_execute=True)

        print(f"Status: {result['status']}")
        print(f"Action: {result.get('action', 'none')}")
        print(f"Message: {result.get('message', '')}")

        if result.get('journal_entry'):
            print(f"Journal: {json.dumps(result['journal_entry'], indent=2)}")

        if result.get('summary'):
            print(f"Summary: {json.dumps(result['summary'], indent=2)}")

        print("-" * 50 + "\n")


if __name__ == "__main__":
    demo_voice_zbar_integration()
