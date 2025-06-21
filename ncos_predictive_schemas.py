"""
NCOS Predictive Engine Schemas
Pydantic models for predictive scoring, feature extraction, and data enrichment
"""

from typing import Literal

from pydantic import BaseModel, Field, validator


class FactorWeights(BaseModel):
    """Defines the weights for various features used in maturity scoring."""
    htf_bias_alignment: float = Field(default=0.2, ge=0.0, le=1.0)
    idm_detected_clarity: float = Field(default=0.1, ge=0.0, le=1.0)
    sweep_validation_strength: float = Field(default=0.15, ge=0.0, le=1.0)
    choch_confirmation_score: float = Field(default=0.15, ge=0.0, le=1.0)
    poi_validation_score: float = Field(default=0.2, ge=0.0, le=1.0)
    tick_density_score: float = Field(default=0.1, ge=0.0, le=1.0)
    spread_stability_score: float = Field(default=0.1, ge=0.0, le=1.0)

    @validator('*')
    def sum_to_one(cls, v, values):
        if len(values) == 6:  # Check when all values are set
            total = sum(values.values()) + v
            if abs(total - 1.0) > 0.01:
                raise ValueError(f"Factor weights must sum to 1.0, got {total}")
        return v

    class Config:
        extra = "allow"

class GradeThresholds(BaseModel):
    """Defines the score thresholds for A, B, C grades."""
    A: float = Field(default=0.85, ge=0.0, le=1.0)
    B: float = Field(default=0.70, ge=0.0, le=1.0)
    C: float = Field(default=0.55, ge=0.0, le=1.0)

    @validator('B')
    def b_less_than_a(cls, v, values):
        if 'A' in values and v >= values['A']:
            raise ValueError("Grade B threshold must be less than Grade A")
        return v

    @validator('C')
    def c_less_than_b(cls, v, values):
        if 'B' in values and v >= values['B']:
            raise ValueError("Grade C threshold must be less than Grade B")
        return v

class ConflictDetectionConfig(BaseModel):
    """Configuration for conflict detection logic."""
    enabled: bool = Field(default=True)
    min_new_setup_maturity_for_conflict_alert: float = Field(default=0.70, ge=0.0, le=1.0)
    suggest_review_trade_if_new_setup_maturity_above: float = Field(default=0.80, ge=0.0, le=1.0)

    @validator('suggest_review_trade_if_new_setup_maturity_above')
    def check_review_threshold(cls, v, values):
        min_alert = values.get('min_new_setup_maturity_for_conflict_alert')
        if min_alert and v < min_alert:
            raise ValueError("Review threshold must be >= alert threshold")
        return v

class PredictiveScorerConfig(BaseModel):
    """Configuration for the PredictiveScorer module."""
    enabled: bool = Field(default=True)
    factor_weights: FactorWeights = Field(default_factory=FactorWeights)
    grade_thresholds: GradeThresholds = Field(default_factory=GradeThresholds)
    min_score_to_emit_potential_entry: float = Field(default=0.65, ge=0.0, le=1.0)
    conflict_detection_settings: ConflictDetectionConfig = Field(default_factory=ConflictDetectionConfig)

class SpreadTrackerConfig(BaseModel):
    """Configuration for spread tracking and stability analysis."""
    enabled: bool = Field(default=True)
    window_size: int = Field(default=25, ge=5)
    high_vol_baseline: float = Field(default=0.0008, gt=0)
    stability_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

class DataEnricherConfig(BaseModel):
    """Configuration for the data enrichment pipeline."""
    enabled: bool = Field(default=True)
    calculate_tick_density: bool = Field(default=True)
    calculate_spread_stability: bool = Field(default=True)
    calculate_htf_alignment: bool = Field(default=True)
    spread_tracker_config: SpreadTrackerConfig = Field(default_factory=SpreadTrackerConfig)

class PredictiveJournalingConfig(BaseModel):
    """Configuration for predictive journaling features."""
    enabled: bool = Field(default=True)
    log_all_evaluations: bool = Field(default=False)
    min_maturity_score_to_log: float = Field(default=0.60, ge=0.0, le=1.0)
    log_format: Literal["json", "yaml", "both"] = Field(default="json")
    log_directory: str = Field(default="logs/predictive_journal")

class FeatureExtractorConfig(BaseModel):
    """Configuration for feature extraction."""
    enabled: bool = Field(default=True)
    use_cached_features: bool = Field(default=True)
    feature_cache_ttl_seconds: int = Field(default=300)

# Composite configuration for the entire predictive system
class PredictiveEngineConfig(BaseModel):
    """Master configuration for the NCOS Predictive Engine."""
    data_enricher: DataEnricherConfig = Field(default_factory=DataEnricherConfig)
    feature_extractor: FeatureExtractorConfig = Field(default_factory=FeatureExtractorConfig)
    predictive_scorer: PredictiveScorerConfig = Field(default_factory=PredictiveScorerConfig)
    journaling: PredictiveJournalingConfig = Field(default_factory=PredictiveJournalingConfig)

    class Config:
        extra = "forbid"
