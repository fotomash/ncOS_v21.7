"""
NCOS Feature Extractor
Extracts and calculates features for predictive scoring from market data
"""

import logging
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import talib

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts features from market data for predictive scoring.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.cache = {}
        self.cache_ttl = self.config.get('feature_cache_ttl_seconds', 300)
        logger.info("FeatureExtractor initialized")

    def extract_features(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame,
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Extract all features needed for predictive scoring.

        Args:
            current_bar: Current bar data
            historical_data: Historical OHLCV data
            context: Additional context (e.g., detected patterns, active trades)

        Returns:
            Dictionary of feature_name -> feature_value (0.0 to 1.0)
        """
        features = {}

        # 1. HTF Bias Alignment
        features['htf_bias_alignment'] = self._calculate_htf_bias_alignment(
            current_bar, historical_data, context
        )

        # 2. Inducement Detection Clarity
        features['idm_detected_clarity'] = self._calculate_idm_clarity(context)

        # 3. Sweep Validation Strength
        features['sweep_validation_strength'] = self._calculate_sweep_strength(
            current_bar, historical_data, context
        )

        # 4. CHoCH Confirmation Score
        features['choch_confirmation_score'] = self._calculate_choch_score(context)

        # 5. POI Validation Score
        features['poi_validation_score'] = self._calculate_poi_validation(
            current_bar, historical_data, context
        )

        # 6. Tick Density Score
        features['tick_density_score'] = self._calculate_tick_density(
            current_bar, context
        )

        # 7. Spread Stability Score
        features['spread_stability_score'] = self._calculate_spread_stability(
            current_bar, historical_data
        )

        # Ensure all features are between 0 and 1
        for key, value in features.items():
            features[key] = max(0.0, min(1.0, float(value)))

        logger.debug(f"Extracted features: {features}")
        return features

    def _calculate_htf_bias_alignment(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame,
            context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate how well the current setup aligns with higher timeframe bias.
        Returns a score from 0.0 to 1.0.
        """
        if context and 'htf_bias' in context:
            current_structure = context.get('structure', 'neutral')
            htf_bias = context['htf_bias']

            if current_structure == htf_bias:
                return 1.0  # Perfect alignment
            elif current_structure == 'neutral':
                return 0.5  # Neutral
            else:
                return 0.2  # Conflicting

        # Fallback: Use simple trend alignment
        if len(historical_data) < 20:
            return 0.5

        sma_20 = historical_data['close'].rolling(20).mean().iloc[-1]
        sma_50 = historical_data['close'].rolling(50).mean().iloc[-1] if len(historical_data) >= 50 else sma_20

        current_price = current_bar['close']

        if current_price > sma_20 > sma_50:
            return 0.8  # Strong bullish alignment
        elif current_price < sma_20 < sma_50:
            return 0.8  # Strong bearish alignment
        else:
            return 0.4  # Mixed signals

    def _calculate_idm_clarity(self, context: Optional[Dict[str, Any]]) -> float:
        """
        Calculate the clarity of inducement detection.
        Based on context provided by the strategy.
        """
        if not context:
            return 0.0

        idm_data = context.get('inducement_data', {})

        if not idm_data:
            return 0.0

        # Factors that contribute to clarity
        has_clear_sweep = idm_data.get('clear_sweep', False)
        multiple_touches = idm_data.get('touch_count', 0) >= 2
        volume_confirmation = idm_data.get('volume_spike', False)

        clarity_score = 0.0
        if has_clear_sweep:
            clarity_score += 0.4
        if multiple_touches:
            clarity_score += 0.3
        if volume_confirmation:
            clarity_score += 0.3

        return clarity_score

    def _calculate_sweep_strength(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame,
            context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate the strength of liquidity sweep validation.
        """
        if not context or 'sweep_data' not in context:
            return 0.0

        sweep_data = context['sweep_data']

        # Factors for sweep strength
        sweep_magnitude = sweep_data.get('magnitude_pips', 0)
        sweep_velocity = sweep_data.get('velocity', 0)  # How fast the sweep occurred
        rejection_strength = sweep_data.get('rejection_strength', 0)

        # Normalize and combine
        magnitude_score = min(sweep_magnitude / 50.0, 1.0)  # Normalize to 50 pips max
        velocity_score = min(sweep_velocity / 5.0, 1.0)  # Normalize to 5 bars

        strength_score = (
                magnitude_score * 0.4 +
                velocity_score * 0.3 +
                rejection_strength * 0.3
        )

        return strength_score

    def _calculate_choch_score(self, context: Optional[Dict[str, Any]]) -> float:
        """
        Calculate the Change of Character (CHoCH) confirmation score.
        """
        if not context or 'choch_data' not in context:
            return 0.0

        choch_data = context['choch_data']

        # CHoCH quality factors
        break_strength = choch_data.get('break_strength', 0)  # How decisively structure was broken
        volume_confirmation = choch_data.get('volume_on_break', False)
        follow_through = choch_data.get('follow_through_bars', 0)

        score = 0.0
        score += min(break_strength, 1.0) * 0.5
        score += 0.3 if volume_confirmation else 0.0
        score += min(follow_through / 3.0, 0.2)  # Max 0.2 for 3+ bars of follow-through

        return score

    def _calculate_poi_validation(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame,
            context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate Point of Interest (POI) validation score.
        """
        if not context or 'poi_data' not in context:
            return 0.0

        poi_data = context['poi_data']

        # POI quality factors
        touches = poi_data.get('historical_touches', 0)
        respect_count = poi_data.get('times_respected', 0)
        confluence_count = poi_data.get('confluence_factors', 0)

        # Calculate score
        touch_score = min(touches / 3.0, 0.3)  # Max 0.3 for 3+ touches
        respect_score = min(respect_count / touches if touches > 0 else 0, 0.4)
        confluence_score = min(confluence_count / 3.0, 0.3)  # Max 0.3 for 3+ confluences

        return touch_score + respect_score + confluence_score

    def _calculate_tick_density(
            self,
            current_bar: pd.Series,
            context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate tick density score as a proxy for liquidity.
        """
        # Use volume as a proxy if tick data not available
        if 'volume' in current_bar and current_bar['volume'] > 0:
            # Normalize volume (this should be calibrated per instrument)
            avg_volume = context.get('avg_volume', 10000) if context else 10000
            density_ratio = current_bar['volume'] / avg_volume

            # Convert to 0-1 score with diminishing returns
            return min(np.log1p(density_ratio) / np.log1p(3), 1.0)

        return 0.5  # Default neutral score

    def _calculate_spread_stability(
            self,
            current_bar: pd.Series,
            historical_data: pd.DataFrame
    ) -> float:
        """
        Calculate spread stability score (inverse of instability).
        More stable spread = higher score.
        """
        if 'spread' not in current_bar or 'spread' not in historical_data.columns:
            return 0.5  # Neutral if no spread data

        if len(historical_data) < 10:
            return 0.5

        # Calculate spread volatility
        recent_spreads = historical_data['spread'].tail(10)
        spread_std = recent_spreads.std()
        spread_mean = recent_spreads.mean()

        if spread_mean > 0:
            # Coefficient of variation (lower is more stable)
            cv = spread_std / spread_mean
            # Convert to stability score (inverse relationship)
            stability_score = 1.0 / (1.0 + cv * 2)  # Scale factor of 2
            return stability_score

        return 0.5
