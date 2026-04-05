import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import analyze

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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cineneuro-api"}
