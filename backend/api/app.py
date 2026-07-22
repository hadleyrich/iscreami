"""FastAPI application with lifespan, CORS, and static file serving."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.types import Receive, Scope, Send

from api.routes import calculate, ingredients, profiles, recipes
from api.settings import settings

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

# Vite builds content-hashed filenames into /assets/ (e.g. index-Bq5G7i4F.js).
# These are immutable — the hash changes when content changes, so cache forever.
_IMMUTABLE_CACHE = b"public, max-age=31536000, immutable"
# index.html must always be revalidated so fresh SPA references roll out.
_SPA_CACHE = b"no-cache"

_CACHE_CONTROL = b"cache-control"


def _with_cache(app: Callable, cache_value: bytes) -> Callable:
    """Wrap an ASGI callable to inject a Cache-Control header on 2xx."""

    async def _wrapped(scope: Scope, receive: Receive, send: Send) -> None:
        async def send_with_cache(message):
            if message.get("type") == "http.response.start":
                status = message.get("status", 0)
                if 200 <= status < 300:
                    headers = list(message.get("headers", []))
                    if not any(k == _CACHE_CONTROL for k, _ in headers):
                        headers.append((_CACHE_CONTROL, cache_value))
                    message["headers"] = headers
            await send(message)

        await app(scope, receive, send_with_cache)

    return _wrapped


class _ImmutableStaticFiles(StaticFiles):
    """StaticFiles serving hashed Vite assets with immutable cache headers."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await _with_cache(super().__call__, _IMMUTABLE_CACHE)(scope, receive, send)


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

# Security headers — defence in depth for all responses (API + SPA)
# SHA-256 hash of the inline anti-FOUC script in frontend/index.html.
# If that script changes, regenerate the hash with:
#   sed -n '/<script>/{:a;n;/</script>/b;H;ba};x;s/\\n//g' frontend/index.html \
#     | openssl dgst -sha256 -binary | base64
_INLINE_THEME_HASH = "sha256-Qs7CjKlg3pe+cAaS/pVGsJaqX+REVCim7a2AbB8z2WA="

CSP = (
    "default-src 'self'; "
    f"script-src 'self' {_INLINE_THEME_HASH}; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "object-src 'none'"
)

PERMISSIONS_POLICY = (
    "geolocation=(), camera=(), microphone=(), payment=(), "
    "usb=(), serial=(), bluetooth=(), autoplay=(), display-capture=()"
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = PERMISSIONS_POLICY
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return response


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
    app.mount(
        "/assets",
        _ImmutableStaticFiles(directory=FRONTEND_DIR / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA index.html for any non-API route."""
        resolved = (FRONTEND_DIR / full_path).resolve()
        if resolved.is_relative_to(FRONTEND_DIR) and resolved.is_file():
            return FileResponse(resolved)
        return FileResponse(
            FRONTEND_DIR / "index.html",
            headers={"Cache-Control": "no-cache"},
        )
