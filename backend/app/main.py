import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import analyze
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="CineNeuro API",
    description="AI-Powered Audience Intelligence Platform — predicts neural responses to movie trailers",
    version="0.1.0",
)

# CORS middleware — allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze.router)

RESULTS_DIR = Path(__file__).parent.parent.parent / "data" / "results"
app.mount("/reports", StaticFiles(directory=str(RESULTS_DIR)), name="reports")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cineneuro-api"}

# Serve React build (must be last — catch-all for frontend routes)
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "build"
if FRONTEND_DIR.exists():
    from fastapi.responses import FileResponse

    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        return FileResponse(str(FRONTEND_DIR / "index.html"))
