"""
Test script for the Predictive Engine
"""

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml

from ncOS.ncos_data_enricher import DataEnricher
from ncOS.ncos_feature_extractor import FeatureExtractor
from ncOS.ncos_predictive_engine import NCOSPredictiveEngine
from ncos_predictive_schemas import PredictiveEngineConfig


def test_predictive_engine():
    """Test the predictive engine with sample data."""

    # Load configuration
    with open('config/predictive_engine_config.yaml', 'r') as f:
        config_dict = yaml.safe_load(f)

    config = PredictiveEngineConfig(**config_dict)

    # Initialize components
    engine = NCOSPredictiveEngine(config)
    extractor = FeatureExtractor()
    enricher = DataEnricher(config.data_enricher)

    # Create sample bar data
    current_bar = pd.Series({
        'timestamp': datetime.now(timezone.utc),
        'open': 2020.5,
        'high': 2025.0,
        'low': 2019.0,
        'close': 2023.5,
        'volume': 15000,
        'spread': 0.5,
        'rsi_14': 35,
        'sma_20': 2025.0,
        'structure': 'bullish'
    })

    # Create sample historical data
    dates = pd.date_range(end=datetime.now(), periods=50, freq='4H')
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.normal(2020, 5, 50),
        'high': np.random.normal(2025, 5, 50),
        'low': np.random.normal(2015, 5, 50),
        'close': np.random.normal(2020, 5, 50),
        'volume': np.random.normal(10000, 2000, 50),
        'spread': np.random.normal(0.5, 0.1, 50)
    })
    historical_data['high'] = historical_data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 2, 50))
    historical_data['low'] = historical_data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 2, 50))

    # Create sample context
    context = {
        'direction': 'buy',
        'structure': 'bullish',
        'htf_bias': 'bullish',
        'inducement_data': {
            'clear_sweep': True,
            'touch_count': 3,
            'volume_spike': True
        },
        'sweep_data': {
            'magnitude_pips': 25,
            'velocity': 2,
            'rejection_strength': 0.8
        },
        'choch_data': {
            'break_strength': 0.9,
            'volume_on_break': True,
            'follow_through_bars': 3
        },
        'poi_data': {
            'historical_touches': 4,
            'times_respected': 3,
            'confluence_factors': 3
        }
    }

    # Extract features
    features = extractor.extract_features(current_bar, historical_data, context)

    print("Extracted Features:")
    for feature, value in features.items():
        print(f"  {feature}: {value:.3f}")

    # Evaluate setup
    evaluation = engine.evaluate_setup(
        timestamp=current_bar['timestamp'],
        symbol='XAUUSD',
        features=features,
        active_trades=[],
        context=context
    )

    print(f"\nEvaluation Result:")
    print(f"  Grade: {evaluation['scoring']['grade']}")
    print(f"  Maturity Score: {evaluation['scoring']['maturity_score']:.3f}")
    print(f"  Potential Entry: {evaluation['scoring']['potential_entry']}")
    print(f"  Recommendation: {evaluation['recommendation']}")

    # Test with conflicting trade
    active_trades = [{
        'id': 'test_trade_1',
        'direction': 'short',  # Opposite direction
        'entry_time': datetime.now()
    }]

    evaluation_with_conflict = engine.evaluate_setup(
        timestamp=current_bar['timestamp'],
        symbol='XAUUSD',
        features=features,
        active_trades=active_trades,
        context=context
    )

    print(f"\nWith Conflict:")
    print(f"  Has Conflict: {evaluation_with_conflict['conflict_analysis']['has_conflict']}")
    if evaluation_with_conflict['conflict_analysis']['has_conflict']:
        conflict = evaluation_with_conflict['conflict_analysis']['conflicts'][0]
        print(f"  Conflict Type: {conflict['conflict_type']}")
        print(f"  Recommendation: {conflict['recommendation']}")

if __name__ == "__main__":
    test_predictive_engine()
