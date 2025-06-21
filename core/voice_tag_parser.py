"""
ncOS Unified v5.0 - Voice Tag Parser
Natural language processing for voice commands and smart tagging
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

import spacy


@dataclass
class VoiceTag:
    """Structured voice tag with extracted entities"""
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    bias: Optional[str] = None
    action: Optional[str] = None
    session: Optional[str] = None
    maturity_score: Optional[float] = None
    notes: Optional[str] = None
    timestamp: str = ""
    raw_text: str = ""
    confidence: float = 0.0


class VoiceTagParser:
    """Parse voice commands into structured tags"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the parser with optional configuration."""
        # Default configuration values
        self.config = {
            "confidence_threshold": 0.7,
            "default_symbol": None,
            "default_timeframe": None,
            "bias_keywords": {
                "bullish": ["bullish", "long", "buy"],
                "bearish": ["bearish", "short", "sell"],
            },
        }

        if config:
            # Merge user supplied configuration
            self.config.update(config)

        # Load spaCy model (can use en_core_web_sm for lighter weight)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None

        # Define patterns for entity extraction
        self.patterns = {
            "symbols": ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "gold", "euro", "cable"],
            "timeframes": ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "1min", "5min", "15min", "hourly", "4hour",
                           "daily"],
            "bias": ["bullish", "bearish", "neutral", "long", "short", "buy", "sell"],
            "sessions": ["london", "new york", "asia", "tokyo", "sydney", "frankfurt"],
            "actions": ["mark", "log", "analyze", "scan", "check", "run", "execute", "monitor"]
        }

        # Normalize patterns to lower case for matching
        self.patterns = {k: [p.lower() for p in v] for k, v in self.patterns.items()}

        # Mapping for common aliases
        self.aliases = {
            "gold": "XAUUSD",
            "euro": "EURUSD",
            "cable": "GBPUSD",
            "1min": "M1",
            "5min": "M5",
            "15min": "M15",
            "hourly": "H1",
            "4hour": "H4",
            "daily": "D1",
            "buy": "bullish",
            "sell": "bearish",
            "long": "bullish",
            "short": "bearish",
            "ny": "new york"
        }

        # Normalize alias keys for case-insensitive lookup
        self.aliases = {k.lower(): v for k, v in self.aliases.items()}

        # Apply bias keywords from configuration
        bias_keywords = self.config.get("bias_keywords") or {}
        if bias_keywords:
            self.patterns["bias"] = sorted({w for words in bias_keywords.values() for w in words})
            for bias, words in bias_keywords.items():
                for word in words:
                    self.aliases[word] = bias

        # Convenience attributes
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.default_symbol = self.config.get("default_symbol")
        self.default_timeframe = self.config.get("default_timeframe")

    def parse(self, voice_input: str) -> VoiceTag:
        """Parse voice input into structured tag"""
        voice_input = voice_input.lower().strip()
        tag = VoiceTag(
            timestamp=datetime.now().isoformat(),
            raw_text=voice_input
        )

        # Extract entities
        tag.symbol = self._extract_symbol(voice_input) or self.default_symbol
        tag.timeframe = self._extract_timeframe(voice_input) or self.default_timeframe
        tag.bias = self._extract_bias(voice_input)
        tag.action = self._extract_action(voice_input)
        tag.session = self._extract_session(voice_input)
        tag.maturity_score = self._extract_maturity(voice_input)
        tag.notes = self._extract_notes(voice_input)

        # Calculate confidence based on extracted entities
        extracted_count = sum(1 for attr in [tag.symbol, tag.timeframe, tag.bias, tag.action] if attr)
        tag.confidence = min(extracted_count / 4.0, 1.0)

        return tag

    def _extract_symbol(self, text: str) -> Optional[str]:
        """Extract trading symbol from text"""
        # Direct pattern matching
        for symbol in self.patterns["symbols"]:
            if symbol in text:
                # Apply alias mapping (symbols stored lower case)
                return self.aliases.get(symbol, symbol.upper())

        # Regex for common forex pairs
        forex_pattern = r"\b([A-Z]{3}/?[A-Z]{3})\b"
        match = re.search(forex_pattern, text.upper())
        if match:
            return match.group(1).replace("/", "")

        return None

    def _extract_timeframe(self, text: str) -> Optional[str]:
        """Extract timeframe from text"""
        for tf in self.patterns["timeframes"]:
            if tf in text:
                return self.aliases.get(tf, tf.upper())

        # Look for patterns like "4 hour" or "15 minute"
        time_pattern = r'(\d+)\s*(min|minute|hour|day)'
        match = re.search(time_pattern, text)
        if match:
            num, unit = match.groups()
            if unit.startswith("min"):
                return f"M{num}"
            elif unit.startswith("hour"):
                return f"H{num}"
            elif unit.startswith("day"):
                return f"D{num}"

        return None

    def _extract_bias(self, text: str) -> Optional[str]:
        """Extract market bias from text"""
        for bias in self.patterns["bias"]:
            if bias in text:
                return self.aliases.get(bias, bias)
        return None

    def _extract_action(self, text: str) -> Optional[str]:
        """Extract action verb from text"""
        for action in self.patterns["actions"]:
            if action in text:
                return action
        return "mark"  # Default action

    def _extract_session(self, text: str) -> Optional[str]:
        """Extract trading session from text"""
        for session in self.patterns["sessions"]:
            if session in text:
                return self.aliases.get(session, session)
        return None

    def _extract_maturity(self, text: str) -> Optional[float]:
        """Extract maturity score if mentioned"""
        # Look for patterns like "maturity 80" or "score 0.8"
        patterns = [
            r'maturity\s*(\d+)',
            r'score\s*(\d*\.?\d+)',
            r'confidence\s*(\d+)%?'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                # Normalize to 0-1 range if needed
                if value > 1:
                    value = value / 100
                return value

        return None

    def _extract_notes(self, text: str) -> Optional[str]:
        """Extract additional notes or context"""
        # Remove known entities to get remaining context
        cleaned = text
        for patterns in self.patterns.values():
            for pattern in patterns:
                cleaned = cleaned.replace(pattern, "")

        # Clean up extra spaces and common words
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        stop_words = ["the", "a", "an", "on", "at", "in", "for", "with", "and", "or"]
        words = [w for w in cleaned.split() if w not in stop_words]

        notes = " ".join(words)
        return notes if notes else None

    def to_journal_entry(self, tag: VoiceTag) -> Dict[str, Any]:
        """Convert voice tag to journal entry format"""
        return {
            "timestamp": tag.timestamp,
            "symbol": tag.symbol or self.default_symbol,
            "timeframe": tag.timeframe or self.default_timeframe,
            "bias": tag.bias,
            "session": tag.session,
            "maturity_score": tag.maturity_score,
            "notes": tag.notes,
            "source": "voice",
            "raw_input": tag.raw_text,
            "confidence": tag.confidence,
            "action": tag.action
        }

    def to_menu_action(self, tag: VoiceTag) -> Dict[str, Any]:
        """Convert voice tag to menu system action"""
        # Map voice actions to menu actions
        action_mapping = {
            "mark": "append_journal",
            "analyze": "run_analysis",
            "scan": "pattern_search",
            "check": "quick_status",
            "run": "execute_strategy",
            "monitor": "start_monitor"
        }

        menu_action = {
            "action": action_mapping.get(tag.action, "append_journal"),
            "params": {
                "symbol": tag.symbol or self.default_symbol,
                "timeframe": tag.timeframe or self.default_timeframe,
                "context": {
                    "bias": tag.bias,
                    "session": tag.session,
                    "maturity_score": tag.maturity_score,
                    "notes": tag.notes
                }
            },
            "source": "voice_command",
            "confidence": tag.confidence
        }

        return menu_action
