# =========================
# Vultr CPU-only Astra Backend
# Robust VirtualEnv Edition
# =========================

# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    git \
    curl \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create virtual environment
RUN python -m venv /opt/venv
# Make sure we use the venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install CPU-only torch FIRST
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining deps (including uvicorn)
RUN pip install --no-cache-dir -r requirements.txt

# -------- Stage 2: Runtime --------
FROM python:3.11-slim

# Runtime deps for torch CPU and others
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
WORKDIR /app

RUN mkdir -p /app/logs /app/astra_memory && chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy app code
COPY --chown=appuser:appuser . .

USER appuser

# Enable venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

# Model cache directory
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:5000/health || exit 1

# Launch using the venv's python and uvicorn module
CMD ["python", "-m", "uvicorn", "main:app", \
    "--host", "0.0.0.0", \
    "--port", "5000", \
    "--timeout-keep-alive", "120", \
    "--timeout-graceful-shutdown", "30", \
    "--workers", "1"]
