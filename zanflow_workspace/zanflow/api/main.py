from fastapi import FastAPI
from zanflow.schemas.agent_profile import AgentProfile
from zanflow.core.executor import execute_trade

app = FastAPI(
    title="ZANFLOW Trading Agent API",
    version="0.1"
)

@app.post("/execute")
def execute(agent: AgentProfile):
    """Run the agent logic based on the provided profile."""
    result = execute_trade(agent.dict())
    return result
