# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG NODE_IMAGE=node:26.13.1-slim@sha256:abe7e5a82b61a8ef67b315b85497c9e65173387ccf2f4a029248184b8e020be5
ARG PYTHON_IMAGE=python:3.15.2-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5

# -------------------------
# Stage 1: Frontend build
# -------------------------
FROM ${NODE_IMAGE} AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install pnpm at the version pinned in frontend/package.json#packageManager.
# Node >= 25 ships without Corepack, so resolve the version explicitly instead
# of relying on `corepack enable`.
RUN PNPM_VERSION="$(node -p 'require("./package.json").packageManager.replace(/^pnpm@/, "")')" \
    && npm install -g "pnpm@${PNPM_VERSION}" \
    && pnpm --version

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
COPY --from=ghcr.io/astral-sh/uv:0.13.10@sha256:a3ea1357342c1a4bf9a0c53a3deb1b55379aefa037338d8113d5771efa01774f /uv /usr/local/bin/uv

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
RUN rm -rf /usr/local/lib/python3.*/site-packages/pip* /usr/local/bin/pip*
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
