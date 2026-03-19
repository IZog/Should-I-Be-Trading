import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import market, scoring

app = FastAPI(
    title="Should I Be Trading?",
    description="Market quality dashboard API",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# API routers (must be before static files catch-all)
app.include_router(market.router, prefix="/api", tags=["market"])
app.include_router(scoring.router, prefix="/api", tags=["scoring"])

# Serve frontend static files in production
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"status": "ok", "app": "Should I Be Trading?", "version": "1.0.0"}
