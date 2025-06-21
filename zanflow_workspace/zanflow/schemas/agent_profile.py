from pydantic import BaseModel
from typing import List, Optional

class ConfirmationConfig(BaseModel):
    type: str  # 'CHoCH' or 'BOS'
    swing_validated: bool

class AgentProfile(BaseModel):
    agent_name: str
    strategy: str
    fractal_ratio: str
    min_rr: float
    entry_zone: str  # 'equilibrium' or 'edge'
    use_inducement_filter: bool
    session_filter: List[str]
    volume_required: bool
    confirmation: ConfirmationConfig
    fallback_strategy: Optional[str]
