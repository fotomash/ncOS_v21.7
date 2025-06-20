#!/usr/bin/env python3
"""
NCOS Voice Journal API Server
Main FastAPI application for voice-enabled trade journal system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import yaml
from pathlib import Path
import logging
from datetime import datetime

# Import routers
from voice_api_routes import router as voice_router
from journal_api import router as journal_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load system configuration from YAML file"""
    config_path = Path("../config/system_config.yaml")
    if not config_path.exists():
        # Use default configuration if file not found
        logger.warning("Configuration file not found, using defaults")
        return {
            "api": {
                "host": "0.0.0.0",
                "port": 8001,
                "title": "NCOS Voice Journal API",
                "version": "1.0.0"
            },
            "journal": {
                "path": "../logs/trade_journal.jsonl"
            }
        }

    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# Load configuration
config = load_config()

# Initialize FastAPI app
app = FastAPI(
    title=config["api"].get("title", "NCOS Voice Journal API"),
    description="Voice-enabled trade journal and analysis system with ZBAR integration",
    version=config["api"].get("version", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice_router, prefix="/voice", tags=["voice"])
app.include_router(journal_router, prefix="/journal", tags=["journal"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NCOS Voice Journal API",
        "version": config["api"].get("version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "voice": "/voice - Voice command processing",
            "journal": "/journal - Journal operations",
            "docs": "/docs - Interactive API documentation",
            "health": "/health - System health check"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if journal file is accessible
        journal_path = Path(config["journal"]["path"])
        journal_exists = journal_path.exists()

        # Check if we can write to journal directory
        journal_dir = journal_path.parent
        can_write = journal_dir.exists() and os.access(journal_dir, os.W_OK)

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "journal_exists": journal_exists,
                "can_write": can_write,
                "api_version": config["api"].get("version", "1.0.0")
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# System info endpoint
@app.get("/info")
async def system_info():
    """Get system information and statistics"""
    try:
        journal_path = Path(config["journal"]["path"])

        # Count journal entries
        entry_count = 0
        if journal_path.exists():
            with open(journal_path, "r") as f:
                entry_count = sum(1 for _ in f)

        return {
            "system": "NCOS Voice Journal",
            "version": config["api"].get("version", "1.0.0"),
            "journal": {
                "path": str(journal_path),
                "entries": entry_count,
                "size_bytes": journal_path.stat().st_size if journal_path.exists() else 0
            },
            "config": {
                "voice_enabled": True,
                "dashboard_enabled": True,
                "api_host": config["api"]["host"],
                "api_port": config["api"]["port"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"The path {request.url.path} was not found",
            "docs": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting NCOS Voice Journal API v{config['api'].get('version', '1.0.0')}")
    logger.info(f"API running on {config['api']['host']}:{config['api']['port']}")
    logger.info(f"Journal path: {config['journal']['path']}")

    # Ensure journal directory exists
    journal_path = Path(config["journal"]["path"])
    journal_path.parent.mkdir(parents=True, exist_ok=True)

    # Create journal file if it doesn't exist
    if not journal_path.exists():
        journal_path.touch()
        logger.info("Created new journal file")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down NCOS Voice Journal API")

# Main entry point
if __name__ == "__main__":
    import os

    # Get host and port from config
    host = config["api"]["host"]
    port = config["api"]["port"]

    # Override with environment variables if set
    host = os.getenv("API_HOST", host)
    port = int(os.getenv("API_PORT", port))

    logger.info(f"🚀 Starting NCOS Voice Journal API on {host}:{port}")
    logger.info(f"📚 Documentation available at http://{host}:{port}/docs")

    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
