# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG NODE_IMAGE=node:24.21.0-slim@sha256:2fe369e969550cde8e867afc3fe370b260140cab4a23d467074295b42163d553
ARG PYTHON_IMAGE=python:3.14.8-slim@sha256:fbecd461fc72d21b2143c6eaba25143738079154a6d0ea3da3aec724f50eed4a

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
COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /usr/local/bin/uv

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
