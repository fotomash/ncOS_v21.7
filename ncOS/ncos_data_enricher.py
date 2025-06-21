"""
NCOS Data Enricher
Enriches market data with additional calculated features and indicators
"""

import logging
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import talib

from ncos_predictive_schemas import DataEnricherConfig, SpreadTrackerConfig

logger = logging.getLogger(__name__)


class SpreadTracker:
    """Tracks spread behavior and calculates stability metrics."""

    def __init__(self, config: SpreadTrackerConfig):
        self.config = config
        self.spread_buffer = []
        self.max_buffer_size = config.window_size
        logger.info(f"SpreadTracker initialized with window size: {config.window_size}")

    def update(self, spread: float) -> Dict[str, float]:
        """Update spread buffer and return stability metrics."""
        self.spread_buffer.append(spread)

        # Maintain buffer size
        if len(self.spread_buffer) > self.max_buffer_size:
            self.spread_buffer.pop(0)

        # Calculate metrics
        if len(self.spread_buffer) < 5:
            return {"stability_score": 0.5, "normalized_spread": spread}

        spreads = np.array(self.spread_buffer)

        # Calculate stability score
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        cv = std_spread / mean_spread if mean_spread > 0 else 0

        # Stability score (inverse of coefficient of variation)
        stability_score = 1.0 / (1.0 + cv * 2)

        # Normalize current spread
        normalized_spread = spread / self.config.high_vol_baseline

        return {
            "stability_score": min(stability_score, 1.0),
            "normalized_spread": normalized_spread,
            "spread_mean": mean_spread,
            "spread_std": std_spread,
            "is_stable": stability_score >= self.config.stability_threshold
        }


class DataEnricher:
    """
    Enriches market data with calculated features for predictive analysis.
    """

    def __init__(self, config: DataEnricherConfig):
        self.config = config
        self.spread_tracker = SpreadTracker(config.spread_tracker_config) if config.calculate_spread_stability else None
        logger.info("DataEnricher initialized")

    def enrich_bar_data(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame,
            context: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """
        Enrich a single bar with calculated features.

        Returns:
            Tuple of (enriched_bar, enrichment_metadata)
        """
        enriched_bar = current_bar.copy()
        metadata = {}

        # 1. Spread stability
        if self.config.calculate_spread_stability and 'spread' in current_bar:
            spread_metrics = self.spread_tracker.update(current_bar['spread'])
            enriched_bar['spread_stability'] = spread_metrics['stability_score']
            enriched_bar['normalized_spread'] = spread_metrics['normalized_spread']
            metadata['spread_metrics'] = spread_metrics

        # 2. HTF Alignment indicators
        if self.config.calculate_htf_alignment and len(historical_data) >= 50:
            htf_alignment = self._calculate_htf_alignment_indicators(current_bar, historical_data)
            for key, value in htf_alignment.items():
                enriched_bar[f'htf_{key}'] = value
            metadata['htf_alignment'] = htf_alignment

        # 3. Tick density proxy (using volume)
        if self.config.calculate_tick_density and 'volume' in current_bar:
            tick_density = self._calculate_tick_density_proxy(current_bar, historical_data)
            enriched_bar['tick_density_score'] = tick_density['score']
            metadata['tick_density'] = tick_density

        # 4. Additional technical indicators for context
        if len(historical_data) >= 20:
            technical_features = self._calculate_technical_features(current_bar, historical_data)
            for key, value in technical_features.items():
                enriched_bar[f'tech_{key}'] = value
            metadata['technical_features'] = technical_features

        return enriched_bar, metadata

    def enrich_dataframe(
            self,
            data: pd.DataFrame,
            context: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Enrich an entire dataframe with calculated features.
        """
        if not self.config.enabled:
            return data

        enriched_data = data.copy()

        # Add moving averages
        if len(data) >= 50:
            enriched_data['sma_20'] = talib.SMA(data['close'], timeperiod=20)
            enriched_data['sma_50'] = talib.SMA(data['close'], timeperiod=50)
            enriched_data['ema_20'] = talib.EMA(data['close'], timeperiod=20)

        # Add volatility indicators
        if len(data) >= 14:
            enriched_data['atr_14'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
            enriched_data['bb_upper'], enriched_data['bb_middle'], enriched_data['bb_lower'] = talib.BBANDS(
                data['close'], timeperiod=20, nbdevup=2, nbdevdn=2
            )

        # Add momentum indicators
        if len(data) >= 14:
            enriched_data['rsi_14'] = talib.RSI(data['close'], timeperiod=14)
            enriched_data['macd'], enriched_data['macd_signal'], enriched_data['macd_hist'] = talib.MACD(
                data['close'], fastperiod=12, slowperiod=26, signalperiod=9
            )

        # Add volume indicators
        if 'volume' in data.columns:
            enriched_data['volume_sma'] = talib.SMA(data['volume'], timeperiod=20)
            enriched_data['volume_ratio'] = data['volume'] / enriched_data['volume_sma']

        logger.info(f"Enriched dataframe with {len(enriched_data.columns) - len(data.columns)} new features")

        return enriched_data

    def _calculate_htf_alignment_indicators(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate indicators for higher timeframe alignment."""
        close_prices = historical_data['close']
        current_close = current_bar['close']

        # Multiple timeframe SMAs
        sma_20 = close_prices.rolling(20).mean().iloc[-1]
        sma_50 = close_prices.rolling(50).mean().iloc[-1]
        sma_100 = close_prices.rolling(100).mean().iloc[-1] if len(close_prices) >= 100 else sma_50

        # Alignment scores
        alignment_score = 0.0
        if current_close > sma_20 > sma_50 > sma_100:
            alignment_score = 1.0  # Perfect bullish alignment
        elif current_close < sma_20 < sma_50 < sma_100:
            alignment_score = 1.0  # Perfect bearish alignment
        else:
            # Partial alignment
            bullish_count = sum([current_close > sma_20, sma_20 > sma_50, sma_50 > sma_100])
            bearish_count = sum([current_close < sma_20, sma_20 < sma_50, sma_50 < sma_100])
            alignment_score = max(bullish_count, bearish_count) / 3.0

        # Trend strength
        trend_strength = abs(sma_20 - sma_50) / sma_50 if sma_50 > 0 else 0

        return {
            "alignment_score": alignment_score,
            "trend_strength": min(trend_strength * 10, 1.0),  # Normalize to 0-1
            "position_vs_sma20": (current_close - sma_20) / sma_20 if sma_20 > 0 else 0
        }

    def _calculate_tick_density_proxy(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate tick density proxy using volume data."""
        if 'volume' not in historical_data.columns:
            return {"score": 0.5, "ratio": 1.0}

        recent_volumes = historical_data['volume'].tail(20)
        avg_volume = recent_volumes.mean()
        current_volume = current_bar['volume']

        if avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            # Convert to score with logarithmic scaling
            score = min(np.log1p(volume_ratio) / np.log1p(3), 1.0)
        else:
            volume_ratio = 1.0
            score = 0.5

        return {
            "score": score,
            "ratio": volume_ratio,
            "percentile": (recent_volumes < current_volume).sum() / len(recent_volumes)
        }

    def _calculate_technical_features(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate additional technical features for context."""
        features = {}

        # Price position within Bollinger Bands
        if all(col in historical_data.columns for col in ['close']):
            close_prices = historical_data['close'].values
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20)

            if not np.isnan(upper[-1]) and upper[-1] != lower[-1]:
                bb_position = (current_bar['close'] - lower[-1]) / (upper[-1] - lower[-1])
                features['bb_position'] = max(0, min(1, bb_position))

        # RSI divergence potential
        if 'rsi_14' in historical_data.columns:
            recent_rsi = historical_data['rsi_14'].tail(5)
            recent_close = historical_data['close'].tail(5)

            if len(recent_rsi) == 5 and not recent_rsi.isna().any():
                # Simple divergence check
                price_trend = 1 if recent_close.iloc[-1] > recent_close.iloc[0] else -1
                rsi_trend = 1 if recent_rsi.iloc[-1] > recent_rsi.iloc[0] else -1

                features['divergence_potential'] = 1.0 if price_trend != rsi_trend else 0.0

        return features
