# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

ARG NODE_IMAGE=node:24.21.0-slim@sha256:2fe369e969550cde8e867afc3fe370b260140cab4a23d467074295b42163d553
ARG PYTHON_IMAGE=python:3.14.7-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

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
COPY --from=ghcr.io/astral-sh/uv:0.12.12@sha256:73d2665b478d8fa2de1cf105c6841f8e9cb6b09e568fc7700440c09f8fcd7ac4 /uv /usr/local/bin/uv

WORKDIR /app

# Create user early (so we can use --chown)
RUN addgroup --system --gid 10001 app \
    && adduser --system --uid 10001 --ingroup app --home /app app

# Copy dependency metadata first (better caching)
COPY --chown=app:app backend/pyproject.toml backend/uv.lock ./backend/

# Install Python deps with cache
RUN --mount=type=cache,target=/root/.cache/uv \
    cd backend && uv sync --no-dev --frozen --no-editable

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
