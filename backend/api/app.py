"""FastAPI application with lifespan, CORS, and static file serving."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import calculate, ingredients, profiles, recipes
from api.settings import settings

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="iscreami",
    description="Ice cream recipe calculator API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all in development; tighten in production via env
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",")]
# allow_credentials=True is rejected by browsers when origins is wildcard
allow_credentials = allowed_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes under /api/v1
api = FastAPI(title="iscreami API")
api.include_router(ingredients.router)
api.include_router(ingredients.cat_router)
api.include_router(recipes.router)
api.include_router(calculate.router)
api.include_router(profiles.router)


from api.schemas import HealthResponse  # noqa: E402


@api.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


app.mount("/api/v1", api)

# Serve frontend static files if the build exists
if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA index.html for any non-API route."""
        resolved = (FRONTEND_DIR / full_path).resolve()
        if resolved.is_relative_to(FRONTEND_DIR) and resolved.is_file():
            return FileResponse(resolved)
        return FileResponse(FRONTEND_DIR / "index.html")
