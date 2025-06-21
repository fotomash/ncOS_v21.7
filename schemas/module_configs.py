from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseModuleConfig(BaseModel):
    """Base configuration object with enabled flag."""

    enabled: bool = True

    class Config:
        extra = "allow"


class DataIngestionConfig(BaseModuleConfig):
    data_source: Optional[str] = None
    symbols: Optional[List[str]] = None


class ContextAnalyzerConfig(BaseModuleConfig):
    bias_determination_timeframes: Optional[List[str]] = None


class LiquidityEngineConfig(BaseModuleConfig):
    lookback_period: Optional[int] = None


class StructureValidatorConfig(BaseModuleConfig):
    swing_engine_config: Dict[str, Any] = Field(default_factory=dict)


class RiskManagerConfig(BaseModuleConfig):
    max_risk_per_trade: Optional[float] = None


class ConfluenceStackerConfig(BaseModuleConfig):
    threshold: Optional[float] = None


class ExecutorConfig(BaseModuleConfig):
    max_concurrent: Optional[int] = None


class JournalerConfig(BaseModuleConfig):
    verbosity: Optional[str] = None
