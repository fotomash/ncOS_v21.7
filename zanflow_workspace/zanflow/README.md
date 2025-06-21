# ZANFLOW Trading Agent Framework

This repository contains a modular AI-driven trading framework combining Wyckoff market phases, Smart Money Concepts, and institutional liquidity dynamics.

## Structure

- **core/**: Python modules implementing each stage of the execution pipeline.
- **schemas/**: Pydantic models for validating agent profiles.
- **api/**: FastAPI application exposing the `/execute` endpoint.
- **profiles/agents/**: YAML configurations defining distinct agent behaviors.

## Getting Started

1. **Install dependencies**

```bash
pip install fastapi pydantic uvicorn
```

2. **Run API**

```bash
uvicorn zanflow.api.main:app --reload
```

3. **Execute an agent**

```bash
POST /execute
Content-Type: application/json

{
  "agent_name": "alpha_sweep_scalper",
  ...
}
```
