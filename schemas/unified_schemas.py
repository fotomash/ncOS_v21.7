from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SessionConfig:
    session_id: str
    token_budget: int
    agents: List[str]
    strategies: List[str]
    memory_config: Dict[str, Any]
