# syntax=docker/dockerfile:1@sha256:87999aa3d42bdc6bea60565083ee17e86d1f3339802f543c0d03998580f9cb89

ARG NODE_IMAGE=node:24.16.0-slim@sha256:242549cd46785b480c832479a730f4f2a20865d61ea2e404fdb2a5c3d3b73ecf
ARG PYTHON_IMAGE=python:3.14.6-slim@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061

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
COPY --from=ghcr.io/astral-sh/uv:0.11.2@sha256:c4f5de312ee66d46810635ffc5df34a1973ba753e7241ce3a08ef979ddd7bea5 /uv /usr/local/bin/uv

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

CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
