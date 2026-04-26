# ══════════════════════════════════════════════════════════════════════════════
# Zariya B2B Marketplace — Dockerfile
# Optimised for Google Cloud Run
# ══════════════════════════════════════════════════════════════════════════════

# ── Base image ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Metadata ───────────────────────────────────────────────────────────────────
LABEL maintainer="Zariya B2B <support@zariya.pk>"
LABEL description="Zariya B2B Marketplace — Streamlit on Cloud Run"

# ── Environment ────────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# ── System deps (minimal) ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps (layer-cached) ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── App source ─────────────────────────────────────────────────────────────────
COPY . .

# ── Streamlit config (Cloud Run needs 0.0.0.0 + port 8080) ────────────────────
RUN mkdir -p /app/.streamlit
COPY .streamlit/config.toml /app/.streamlit/config.toml

# ── Non-root user (security best practice) ────────────────────────────────────
RUN useradd --create-home --shell /bin/bash zariya \
    && chown -R zariya:zariya /app
USER zariya

# ── Health check ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# ── Expose & run ───────────────────────────────────────────────────────────────
EXPOSE 8080

CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]
