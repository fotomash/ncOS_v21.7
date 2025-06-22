# zanlink/main.py

"""
Main ZanLink FastAPI entry point. Mounts all API routes and exposes health check.
This app can be run via Uvicorn or served in Docker.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from zanlink.routes import events

app = FastAPI(title="ZanLink API", version="0.1")

# Allow all origins for dev (can restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/status")
def status():
    return {"status": "online", "message": "ZanLink API is running"}

# Mount routers
app.include_router(events.router, tags=["Events"])
