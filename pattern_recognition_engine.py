"""Advanced pattern recognition using vector similarity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass
class PatternMatch:
    """Represents a matched pattern."""

    pattern_type: str
    confidence: float
    timeframe: str
    start_time: datetime
    end_time: datetime
    metadata: Dict


class PatternRecognitionEngine:
    """Advanced pattern recognition using vector similarity."""

    def __init__(self, vector_client: any) -> None:
        self.vector_client = vector_client
        self.pattern_library = self._load_pattern_library()

    def _load_pattern_library(self) -> Dict[str, np.ndarray]:
        """Load Zanflow pattern library."""
        return {
            # Price Action Patterns
            "bullish_engulfing": np.array([0.2, 0.8, 0.1, 0.9, 0.3]),
            "bearish_engulfing": np.array([0.8, 0.2, 0.9, 0.1, 0.7]),
            "morning_star": np.array([0.1, 0.3, 0.8, 0.9, 0.2]),
            "evening_star": np.array([0.9, 0.7, 0.2, 0.1, 0.8]),
            # SMC Patterns
            "breaker_block": np.array([0.5, 0.9, 0.3, 0.8, 0.4]),
            "order_block": np.array([0.7, 0.4, 0.9, 0.3, 0.6]),
            "fair_value_gap": np.array([0.3, 0.8, 0.5, 0.7, 0.9]),
            "liquidity_void": np.array([0.6, 0.2, 0.8, 0.4, 0.5]),
            # Market Structure
            "higher_high": np.array([0.1, 0.4, 0.7, 0.9, 0.8]),
            "lower_low": np.array([0.9, 0.6, 0.3, 0.1, 0.2]),
            "break_of_structure": np.array([0.5, 0.8, 0.6, 0.9, 0.7]),
            "change_of_character": np.array([0.7, 0.5, 0.9, 0.6, 0.8]),
            # Wyckoff Patterns
            "accumulation": np.array([0.3, 0.4, 0.6, 0.8, 0.9]),
            "distribution": np.array([0.9, 0.8, 0.6, 0.4, 0.3]),
            "spring": np.array([0.2, 0.1, 0.8, 0.9, 0.7]),
            "upthrust": np.array([0.8, 0.9, 0.2, 0.1, 0.3]),
        }

    def detect_patterns(self, market_data: pd.DataFrame, timeframe: str = "5m") -> List[PatternMatch]:
        """Detect patterns in market data."""
        patterns: List[PatternMatch] = []
        price_vectors = self._create_price_vectors(market_data)

        for idx, vector in enumerate(price_vectors):
            self.vector_client.upsert(
                collection="price_patterns",
                id=f"price_{timeframe}_{idx}",
                vector=vector.tolist(),
                metadata={
                    "timeframe": timeframe,
                    "timestamp": market_data.index[idx].isoformat(),
                },
            )

        for pattern_name, pattern_vector in self.pattern_library.items():
            results = self.vector_client.query(
                collection="price_patterns",
                vector=pattern_vector.tolist(),
                top_k=5,
                min_score=0.75,
            )

            for result in results:
                if result["score"] > 0.8:
                    patterns.append(
                        PatternMatch(
                            pattern_type=pattern_name,
                            confidence=result["score"],
                            timeframe=timeframe,
                            start_time=datetime.fromisoformat(result["metadata"]["timestamp"]),
                            end_time=datetime.fromisoformat(result["metadata"]["timestamp"]),
                            metadata={"vector_id": result["id"]},
                        )
                    )

        return patterns

    def _create_price_vectors(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Convert price data to normalized vectors."""
        vectors: List[np.ndarray] = []
        window_size = 5

        for i in range(len(data) - window_size):
            window = data.iloc[i : i + window_size]

            open_norm = (window["open"] - window["open"].min()) / (
                window["open"].max() - window["open"].min() + 1e-8
            )
            high_norm = (window["high"] - window["high"].min()) / (
                window["high"].max() - window["high"].min() + 1e-8
            )
            low_norm = (window["low"] - window["low"].min()) / (
                window["low"].max() - window["low"].min() + 1e-8
            )
            close_norm = (window["close"] - window["close"].min()) / (
                window["close"].max() - window["close"].min() + 1e-8
            )
            volume_norm = (window["volume"] - window["volume"].min()) / (
                window["volume"].max() - window["volume"].min() + 1e-8
            )

            vector = np.array(
                [
                    open_norm.mean(),
                    high_norm.mean(),
                    low_norm.mean(),
                    close_norm.mean(),
                    volume_norm.mean(),
                ]
            )

            vectors.append(vector)

        return vectors

    def learn_pattern(self, pattern_data: pd.DataFrame, pattern_name: str, pattern_type: str) -> None:
        """Learn new pattern from labeled data."""
        vectors = self._create_price_vectors(pattern_data)
        if not vectors:
            return

        pattern_vector = np.mean(vectors, axis=0)

        self.vector_client.upsert(
            collection="learned_patterns",
            id=f"learned_{pattern_name}",
            vector=pattern_vector.tolist(),
            metadata={
                "pattern_name": pattern_name,
                "pattern_type": pattern_type,
                "learned_at": datetime.now().isoformat(),
                "confidence": 0.95,
            },
        )

        self.pattern_library[pattern_name] = pattern_vector
