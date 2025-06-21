"""
NCOS v21 Unified Pydantic Schemas
Generated from architecture analysis
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Base Models
class NCOSBaseModel(BaseModel):
    """Base model for all NCOS components"""
    id: Optional[str] = Field(None, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = Field("21.0", description="NCOS version")

    class Config:
        extra = "forbid"
        validate_assignment = True

# Agent Models
class AgentRole(str, Enum):
    DATA_INGESTION = "data_ingestion"
    STRATEGY = "strategy"
    VISUALIZATION = "visualization"
    MEMORY_VECTOR = "memory_vector"
    ORCHESTRATION = "orchestration"
    PROMPT_OPTIMIZATION = "prompt_optimization"

class AgentSpec(NCOSBaseModel):
    """Unified agent specification"""
    name: str = Field(..., description="Agent name")
    role: AgentRole = Field(..., description="Agent role")
    capabilities: List[str] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    memory_namespace: str = Field(..., description="Memory isolation namespace")
    single_session_safe: bool = Field(True)
    max_token_usage: int = Field(2048)

# Memory Models
class MemoryLayer(str, Enum):
    L1_SESSION = "L1_session"
    L2_VECTOR = "L2_vector"
    L3_PERSISTENT = "L3_persistent"

class MemoryNamespace(NCOSBaseModel):
    """Memory namespace configuration"""
    namespace: str = Field(..., description="Unique namespace identifier")
    layer: MemoryLayer = Field(...)
    isolation: str = Field("agent_scoped")
    max_size_mb: int = Field(256)
    vector_enabled: bool = Field(False)
    compression_ratio: float = Field(0.75)

# Session Models
class SessionState(NCOSBaseModel):
    """Session state management"""
    session_id: str = Field(..., description="Unique session identifier")
    workspace_config: Dict[str, Any] = Field(default_factory=dict)
    active_agents: List[str] = Field(default_factory=list)
    memory_usage: Dict[str, float] = Field(default_factory=dict)
    token_budget: int = Field(8192)
    token_used: int = Field(0)

# Financial Strategy Models
class WyckoffPhase(str, Enum):
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"

class StrategyConfig(NCOSBaseModel):
    """Trading strategy configuration"""
    strategy_type: str = Field(..., description="Strategy identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_profile: str = Field("moderate")
    enabled: bool = Field(True)
    wyckoff_phases: List[WyckoffPhase] = Field(default_factory=list)

# Data Models
class DataSource(NCOSBaseModel):
    """Data source configuration"""
    source_type: str = Field(..., description="api|file|stream")
    format: str = Field(..., description="csv|parquet|json")
    enrichment_enabled: bool = Field(True)
    real_time: bool = Field(False)
    connection_params: Dict[str, Any] = Field(default_factory=dict)

# Charting Models
class ChartConfig(NCOSBaseModel):
    """Native charting configuration"""
    chart_type: str = Field(..., description="Chart type identifier")
    action_hooks: List[str] = Field(default_factory=list)
    interactive: bool = Field(True)
    export_formats: List[str] = Field(default=["png", "svg", "json"])
    extensible: bool = Field(True)
