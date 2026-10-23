# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Production-oriented Dockerfile for Saphira AI monorepo
# Goal: turnkey, buyer-ready container for due diligence and deployment

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY pyproject.toml requirements.txt* ./
RUN pip install --upgrade pip \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
    && pip install -e .

# Copy application code
COPY . .

# Non-root user for security
RUN useradd --create-home --shell /bin/bash saphira \
    && chown -R saphira:saphira /app
USER saphira

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command — adjust entrypoint if your ASGI app path differs
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
