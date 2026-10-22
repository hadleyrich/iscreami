# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG NODE_IMAGE=node:24.22.1-slim@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205
ARG PYTHON_IMAGE=python:3.15.1-slim@sha256:08275f764e022331c6d3e3ca55d8cce01fa4684b02111adf0445d71806fe7941

# -------------------------
# Stage 1: Frontend build
# -------------------------
FROM ${NODE_IMAGE} AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Use pnpm version from frontend/package.json#packageManager via Corepack
RUN corepack enable

# Install deps with cache
RUN --mount=type=cache,target=/root/.pnpm-store \
    pnpm install --frozen-lockfile

# Copy source and build
COPY frontend/ ./
RUN pnpm build

# -------------------------
# Stage 2: Runtime
# -------------------------
FROM ${PYTHON_IMAGE} AS runtime

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /usr/local/bin/uv

WORKDIR /app

# Create user early (so we can use --chown)
RUN addgroup --system --gid 10001 app \
    && adduser --system --uid 10001 --ingroup app --home /app app

# Copy dependency metadata first (better caching)
COPY --chown=app:app backend/pyproject.toml backend/uv.lock ./backend/

# Install Python deps with cache.
# --no-build forces wheels only: the slim image has no C/Rust toolchain, so a
# dependency without a wheel for the pinned CPython must fail here rather than
# silently falling back to building from source (which is what broke the
# Python 3.15 bump: pydantic-core had no cp315 wheel and maturin could not
# find a linker).
RUN --mount=type=cache,target=/root/.cache/uv \
    cd backend && uv sync --no-dev --no-build --frozen --no-editable

# Copy backend source
COPY --chown=app:app backend/ ./backend/

# Copy frontend build output
COPY --from=frontend-build --chown=app:app /app/frontend/dist ./frontend/dist

# Switch to non-root user
USER app

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PATH=/app/backend/.venv/bin:${PATH} \
    PORT=8000

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,sys,urllib.request; port=os.getenv('PORT','8000'); sys.exit(0 if urllib.request.urlopen(f'http://localhost:{port}/health').getcode()==200 else 1)"

CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000} --no-server-header"]
