"""
Core schemas and base classes for NCOS v11.5 Phoenix-Mesh.

This module defines the core data models used throughout the system,
including configuration schemas, agent profiles, and messaging.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from enum import Enum
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field, validator, root_validator

class MemoryTier(str, Enum):
    """Memory tier enumeration."""
    L1_SESSION = "L1_session"
    L2_VECTOR = "L2_vector"
    L3_PERSISTENT = "L3_persistent"

class AgentType(str, Enum):
    """Agent type enumeration."""
    STRATEGY = "strategy"
    ANALYSIS = "analysis"
    DATA_INGESTION = "data_ingestion"
    VISUALIZATION = "visualization"
    ORCHESTRATION = "orchestration"
    MEMORY = "memory"
    SYSTEM = "system"

class MessageType(str, Enum):
    """Message type enumeration."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    ACTION = "action"
    RESULT = "result"
    ERROR = "error"

class TokenBudget(BaseModel):
    """Token budget model."""
    total: int
    used: int = 0
    reserved: int = 0

    @property
    def available(self) -> int:
        """Calculate available tokens."""
        return max(0, self.total - self.used - self.reserved)

    @property
    def usage_percentage(self) -> float:
        """Calculate token usage percentage."""
        if self.total == 0:
            return 0
        return (self.used / self.total) * 100

class MemoryConfig(BaseModel):
    """Memory system configuration."""
    vector_db_type: Literal["faiss", "pinecone", "milvus"] = "faiss"
    connection_string: Optional[str] = None
    vector_dimension: int = 768
    similarity_threshold: float = 0.75
    max_items_per_query: int = 50
    cache_size_mb: int = 100
    snapshot_dir: str = "./snapshots"
    snapshot_interval_seconds: int = 300
    namespaces: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class AgentTrigger(BaseModel):
    """Agent trigger configuration."""
    name: str
    type: str
    priority: int = 0
    condition: Optional[str] = None

class AgentCapability(BaseModel):
    """Agent capability definition."""
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

class AgentMemoryAccess(BaseModel):
    """Agent memory access configuration."""
    namespace: str
    tier: MemoryTier
    access_type: Literal["read", "write", "read_write"] = "read_write"
    ttl_seconds: Optional[int] = None

class AgentProfile(BaseModel):
    """Agent profile definition."""
    id: str
    name: str
    description: str
    version: str
    type: AgentType
    capabilities: List[AgentCapability] = Field(default_factory=list)
    triggers: List[AgentTrigger] = Field(default_factory=list)
    memory_access: List[AgentMemoryAccess] = Field(default_factory=list)
    token_budget: int = 1000
    timeout_seconds: int = 30
    max_consecutive_errors: int = 3
    auto_recovery: bool = True
    dependencies: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)

    @validator("id")
    def id_must_be_valid(cls, v):
        """Validate agent ID format."""
        if not v or " " in v:
            raise ValueError("Agent ID must not contain spaces")
        return v

class AgentConfig(BaseModel):
    """Agent configuration in the system config."""
    id: str
    profile_path: str
    enabled: bool = True
    token_budget_override: Optional[int] = None
    config_overrides: Dict[str, Any] = Field(default_factory=dict)

class TokenBudgetConfig(BaseModel):
    """Token budget configuration."""
    total: int = 8000
    reserve_percentage: float = 0.2
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95

class SystemConfig(BaseModel):
    """System configuration schema."""
    system_name: str = "NCOS Phoenix"
    system_version: str = "11.5.0"
    session_id: Optional[str] = None
    log_level: str = "INFO"

    # Paths
    agent_profiles_dir: str = "config/agent_profiles"
    workspace_dir: str = "./workspace"

    # Token budget
    token_budget: TokenBudgetConfig = Field(default_factory=TokenBudgetConfig)

    # Memory configuration
    memory: MemoryConfig = Field(default_factory=MemoryConfig)

    # Snapshot configuration
    snapshot_interval_seconds: int = 300

    # Agents
    agents: List[AgentConfig] = Field(default_factory=list)

    # Advanced settings
    debug_mode: bool = False
    hot_reload: bool = False
    performance_monitoring: bool = True

class Message(BaseModel):
    """Message model for agent communication."""
    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    type: MessageType
    content: Union[str, Dict[str, Any]]
    sender: str
    receiver: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Action(BaseModel):
    """Action model for system execution."""
    id: str = Field(default_factory=lambda: f"action_{uuid4().hex[:8]}")
    agent_id: str
    capability: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    priority: int = 0
    deadline: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ActionResult(BaseModel):
    """Result of an action execution."""
    action_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    token_usage: int = 0
    execution_time: float = 0
    memory_operations: List[Dict[str, Any]] = Field(default_factory=list)
