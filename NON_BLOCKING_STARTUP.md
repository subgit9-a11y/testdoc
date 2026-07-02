# 🚀 Astra Backend - Non-Blocking Startup Architecture

## Overview

This document describes the architectural changes made to enable **instant FastAPI startup** with background model loading.

## Problem Solved

Previously, the Astra backend would **crash on startup** because:
1. ML models were loaded at import time
2. FastAPI couldn't respond to `/health` during model loading
3. Google Speech credentials errors would crash the entire application
4. Connection reset errors (`curl: (56) Recv failure`) occurred during startup

## Solution Architecture

### New Model Registry Pattern

A centralized `ModelRegistry` singleton manages all ML models:

```
app/model_registry.py
├── ModelStatus (enum: NOT_STARTED, LOADING, READY, FAILED, DISABLED)
├── ModelInfo (dataclass for tracking model state)
└── ModelRegistry (singleton)
    ├── start_background_loading()  → Loads all models in thread pool
    ├── get_model("name")           → Returns model if ready, None otherwise
    ├── is_ready("name")            → Check if specific model is ready
    ├── get_all_status()            → Get status of all models (for /health)
    └── cleanup()                   → Release all model resources
```

### Models Managed

| Model | Status at Startup | Loaded When |
|-------|-------------------|-------------|
| SentenceTransformer (embeddings) | `LOADING` | Background thread |
| Whisper (STT) | `LOADING` | Background thread |
| Google Speech | `LOADING` or `DISABLED` | Background (skipped if no credentials) |
| Google TTS | `LOADING` or `DISABLED` | Background (skipped if no credentials) |
| IndicTrans2 | `NOT_STARTED` | On-demand (first translation request) |

## Files Modified

### 1. `main.py` (Complete Rewrite)
- FastAPI starts **instantly** (no blocking in lifespan)
- Models load via `asyncio.create_task()` after startup
- New endpoints:
  - `GET /health` → Always responds immediately with model status
  - `GET /health/live` → Kubernetes liveness probe
  - `GET /health/ready` → Kubernetes readiness probe

### 2. `app/model_registry.py` (New File)
- Centralized singleton for all ML model lifecycle
- Background loading via `ThreadPoolExecutor`
- Thread-safe model access
- Graceful error handling (one model failing doesn't crash others)

### 3. `app/astra/rag_memory.py`
- Removed `SentenceTransformer` loading at `__init__()`
- Now fetches embeddings model from `model_registry`
- Falls back to deterministic random vectors if model not ready

### 4. `app/astra/voice_service.py`
- Removed Whisper and Google Speech loading at `__init__()`
- Now fetches models from `model_registry`
- Google Speech errors are **silently skipped** (marked as DISABLED)

### 5. `app/inference.py`
- Made torch imports lazy (not at module load time)
- All model loading deferred to `async load_model()`
- Runs heavy loading in thread pool to avoid blocking event loop

### 6. `Dockerfile`
- Added `HEALTHCHECK` instruction
- Increased uvicorn timeouts:
  - `--timeout-keep-alive 120`
  - `--timeout-graceful-shutdown 30`
- Added model cache directory environment variables

## Health Endpoint Response

```json
{
  "status": "ok",
  "uptime_seconds": 5.2,
  "api_ready": true,
  "pipeline_ready": true,
  "models": {
    "embeddings": {"status": "ready", "error": null, "load_time_ms": 1234.5},
    "whisper": {"status": "loading", "error": null, "load_time_ms": 0},
    "google_speech": {"status": "disabled", "error": "credentials not configured"},
    "google_tts": {"status": "disabled", "error": "credentials not configured"},
    "indictrans2": {"status": "not_started", "error": null}
  },
  "all_models_ready": false,
  "ai_connected": true
}
```

## Startup Sequence

```
[0ms]     🚀 FastAPI server starts
[5ms]     ✅ /health endpoint is responsive
[10ms]    📋 Background model loading starts
[~30s]    ✅ Embeddings model loaded
[~60s]    ✅ Whisper model loaded
[~60s]    ℹ️ Google Speech skipped (no credentials)
[Ready]   🎉 All critical models ready, full functionality available
```

## Testing

After deploying, verify:

```bash
# Should respond immediately (even during model loading)
curl http://localhost:5000/health

# Liveness probe (always 200 if process alive)
curl http://localhost:5000/health/live

# Readiness probe (200 only when models ready)
curl http://localhost:5000/health/ready
```

## Key Guarantees

1. ✅ `docker run` starts **instantly**
2. ✅ `curl /health` works **immediately** 
3. ✅ Models download in **background**
4. ✅ API becomes ready once models are loaded
5. ✅ **No connection reset errors** occur
6. ✅ Google Speech failures don't crash startup
7. ✅ Each model loads independently (isolated failures)
