"""
orchestrator.py: ZSI Copilot Orchestrator Core – final pro-level ready version.
Handles API routing, security, telemetry, dynamic memory backend selection, and agent dispatch.
"""
import importlib
import logging
import os
import pkgutil
from datetime import datetime
from typing import Callable, Dict

import yaml
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from pythonjsonlogger import jsonlogger

from schema.models import Intent, ResponseModel

"""
orchestrator.py: ZSI Copilot Orchestrator Core – final pro-level ready version. Handles API routing, security, telemetry, and dynamic agent dispatch.
"""

# Environment & Config
ENV = os.getenv("ZSI_ENV", "development")
CONFIG_PATH = os.getenv("ZSI_CONFIG_PATH", "zsi_config.yaml")
logger = logging.getLogger("zsi.orchestrator")

# Configure structured JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

try:
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f) or {}
except FileNotFoundError:
    logger.warning(f"Config file not found at {CONFIG_PATH}, falling back to env vars")
    cfg = {}

LOG_LEVEL = os.getenv("ZSI_LOG_LEVEL", cfg.get("log_level", "INFO")).upper()
logger.setLevel(LOG_LEVEL)
logger.info(f"Log level set to: {LOG_LEVEL}")
logger.info(f"Environment: {ENV}")

# Config overrides
API_PREFIX = os.getenv("ZSI_API_PREFIX", cfg.get("api_prefix", "/api"))
MEMORY_BACKEND = os.getenv("ZSI_MEMORY_BACKEND", cfg.get("memory_backend", "json"))
EXPECTED_API_KEY = os.getenv("ZSI_API_KEY", cfg.get("api_key"))

# Set MODULES_PATH from env var ZSI_MODULES_PATH, or config, or default
MODULES_PATH = os.getenv("ZSI_MODULES_PATH", cfg.get("modules_path", os.path.join(os.path.dirname(__file__), "..", "modules")))
logger.info(f"Modules path set to: {MODULES_PATH}")

if ENV == "production":
    CORS_ORIGINS = cfg.get("cors_origins", [])
else:
    CORS_ORIGINS = cfg.get("cors_origins", ["*"])

# Dynamic Hosting & Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", cfg.get("database_url", "sqlite:///data.db"))
HOSTING_TIERS = cfg.get("hosting_tiers", {
    "mvp": {"provider": "railway", "db": "json"},
    "scale": {"provider": "firebase", "db": "dynamo"},
    "prod": {"provider": "aws_lambda", "db": "dynamodb"}
})

# OpenTelemetry setup
resource = Resource(attributes={"service.name": "zsi-copilot"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Global Dependencies
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if not EXPECTED_API_KEY or x_api_key != EXPECTED_API_KEY:
        logger.warning("Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")

jwt_scheme = HTTPBearer(auto_error=True)
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme)):
    if not credentials or credentials.scheme.lower() != "bearer":
        logger.warning("Missing or invalid JWT token")
        raise HTTPException(status_code=401, detail="Invalid JWT")
    token = credentials.credentials
    # TODO: Add JWT validation logic here

# FastAPI App init
app = FastAPI(
    title=cfg.get("openapi_title", "ZSI Copilot Orchestrator"),
    version=cfg.get("openapi_version", "1.0.0"),
    description=cfg.get("openapi_description", "Scalable, pluggable orchestration layer for AI agents"),
    openapi_tags=cfg.get("openapi_tags", [{"name": "Orchestrator", "description": "Routing and core services"}]),
    docs_url=cfg.get("docs_url", f"{API_PREFIX}/docs"),
    redoc_url=cfg.get("redoc_url", f"{API_PREFIX}/redoc"),
    openapi_url=cfg.get("openapi_url", f"{API_PREFIX}/openapi.json"),
    dependencies=[Depends(verify_api_key)]
)

# Log the docs and OpenAPI URLs
logger.info(f"API docs available at {app.docs_url}, redoc at {app.redoc_url}, spec at {app.openapi_url}")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Instrument
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
logger.info("OpenTelemetry instrumentation initialized")

# TODO: Add Prometheus metrics instrumentation when ready


# Memory backend: select based on MEMORY_BACKEND
if MEMORY_BACKEND.lower() == "dynamodb":
    from core.aws_memory import load_user_memory, save_user_memory
else:
    from core.memory import load_user_memory, save_user_memory

logger.info(f"Using database endpoint: {DATABASE_URL}")
logger.info(f"Hosting tiers configured: {list(HOSTING_TIERS.keys())}")

# Dynamic agent discovery
agent_registry: Dict[str, Callable] = {}
for finder, name, ispkg in pkgutil.iter_modules([MODULES_PATH]):
    try:
        module = importlib.import_module(f"modules.{name}.agent")
        handler = getattr(module, "handle_intent", None)
        if handler:
            agent_registry[name] = handler
            logger.info(f"Registered agent '{name}'")
    except ImportError as e:
        logger.debug(f"Failed to load agent '{name}': {e}")

logger.info(f"Agents available: {list(agent_registry.keys())}")

# Router setup
router = APIRouter(prefix=API_PREFIX, dependencies=[Depends(verify_api_key), Depends(verify_jwt)])

@router.get("/health", summary="Health Check")
async def health() -> dict:
    return {"status": "ok", "env": ENV}

@router.post("/process", response_model=ResponseModel, summary="Process Intent")
async def process_intent(intent: Intent, request: Request) -> ResponseModel:
    span = tracer.start_as_current_span("process_intent")
    span.set_attribute("agent.count", len(agent_registry))
    user_id = intent.user_id or "anonymous"
    ts = intent.timestamp or datetime.utcnow().isoformat()
    date = ts.split("T")[0]

    # Load memory
    memory = load_user_memory(user_id, date)

    # Dispatch to agent
    key = intent.business_type or intent.agent
    handler = agent_registry.get(key)
    if not handler:
        logger.error(f"No handler for key '{key}'")
        raise HTTPException(status_code=400, detail=f"No agent found for '{key}'")

    try:
        response = handler(intent, memory)
        save_user_memory(user_id, date, memory)
        return response
    except Exception as err:
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=str(err))

FUTURE_HOOKS = [
    "Auth Flows: OAuth2, role-based access control",
    "Deployment: AWS Lambda handler wrapper, Kubernetes readiness/liveness probes",
    "Feature Flags: integrate with LaunchDarkly or Flagsmith",
    "Hosting Tier Switch: auto-select backend based on ENV and HOSTING_TIERS",
    "Logging: JSON logger, correlation IDs, Sentry integration",
    "Metrics: Prometheus endpoint, custom counters",
    "Database Migration: integrate Alembic or similar for SQL backends"
]

@app.on_event("startup")
async def startup_event():
    logger.info(f"Startup: Loaded agents: {list(agent_registry.keys())}")
    logger.info(f"Startup: Future hooks planned: {FUTURE_HOOKS}")

app.include_router(router)

# End of orchestrator.py — ready for further extension
