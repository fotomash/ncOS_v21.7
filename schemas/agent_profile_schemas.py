from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentProfileSchema(BaseModel):
    """Schema for individual agent profile configuration."""

    profile_name: str
    description: Optional[str] = None
    version: str = Field(default="1.0.0")
    execution_sequence: List[str] = Field(default_factory=list)
    code_map: Dict[str, str] = Field(default_factory=dict)
    meta_agent: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"

