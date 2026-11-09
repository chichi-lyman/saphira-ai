# Saphira Frontier Verifier — multi-stage image
# © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella

FROM rust:1.78-slim AS rust-builder
WORKDIR /usr/src/verifier
RUN apt-get update && apt-get install -y --no-install-recommends pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*
COPY crates/saphira_symbolic_verifier/Cargo.toml ./
COPY crates/saphira_symbolic_verifier/src ./src
# Build native lib when crate is complete; ignore failure on minimal scaffold
RUN cargo build --release || true

FROM python:3.11-slim AS runner
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    SAPHIRA_HOME=/app \
    PYTHONPATH=/app

WORKDIR ${SAPHIRA_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq-dev libgmp-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/frontier/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/frontier ./src/frontier
COPY deploy/frontier/entrypoint.sh ${SAPHIRA_HOME}/entrypoint.sh
RUN chmod +x ${SAPHIRA_HOME}/entrypoint.sh && ldconfig || true

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
