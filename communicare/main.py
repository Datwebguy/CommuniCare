"""
Main entrypoint for CommuniCare application.
Configures FastAPI, CORS middleware, static asset serving, and server lifecycle.
Serves Superhuman-style landing page at `/` and interactive studio at `/app`.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables from .env if present
load_dotenv()

from communicare.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("communicare.main")

app = FastAPI(
    title="CommuniCare Agent",
    description="Autonomous Agent Pipeline converting caregiver messages into high-contrast AAC picture symbol boards.",
    version="1.0.0"
)

# Enable CORS for local development and web embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

# Mount static web UI files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
@app.get("/landing")
def serve_landing_page():
    """Serve Superhuman-style editorial landing page."""
    landing_file = static_dir / "landing.html"
    if landing_file.exists():
        return FileResponse(landing_file)
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "CommuniCare Agent API is active.",
        "documentation": "/docs",
        "health": "/api/health"
    }


@app.get("/app")
def serve_studio_app():
    """Serve interactive CommuniCare AAC Board Studio."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "CommuniCare Agent API is active.",
        "documentation": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("communicare.main:app", host=host, port=port, reload=True)
