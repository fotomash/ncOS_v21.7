from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SpreadTrackerConfig:
    """Configuration for the SpreadTracker."""
    window_size: int = 50
    high_vol_baseline: float = 0.5
    stability_threshold: float = 0.75

@dataclass
class DataEnricherConfig:
    """Configuration for DataEnricher processing."""
    enabled: bool = True
    calculate_spread_stability: bool = True
    calculate_htf_alignment: bool = True
    calculate_tick_density: bool = True
    spread_tracker_config: SpreadTrackerConfig = field(default_factory=SpreadTrackerConfig)
