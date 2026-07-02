"""
Astra Model Registry - Centralized Model Lifecycle Management

This module provides a singleton registry for all ML models used in the Astra backend.
Models are loaded asynchronously in background threads, ensuring:
- FastAPI starts instantly
- /health endpoint is always responsive
- No duplicate model loading
- Graceful error handling

MODELS MANAGED:
- SentenceTransformer (embeddings for RAG)
- Whisper (speech-to-text)
- IndicTrans2 (translation)
- Google Speech clients (optional)

Usage:
    from app.model_registry import model_registry
    
    # Check if model is ready
    if model_registry.is_ready("embeddings"):
        model = model_registry.get_model("embeddings")
"""

import logging
import threading
import asyncio
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model loading status"""
    NOT_STARTED = "not_started"
    LOADING = "loading"
    READY = "ready"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ModelInfo:
    """Information about a registered model"""
    name: str
    status: ModelStatus = ModelStatus.NOT_STARTED
    model: Any = None
    error: Optional[str] = None
    load_time_ms: float = 0.0
    started_at: Optional[float] = None


class ModelRegistry:
    """
    Centralized singleton registry for all ML models.
    
    Features:
    - Background loading in thread pool
    - Status tracking for each model
    - Safe access with readiness checks
    - Error isolation (one model failing doesn't crash others)
    """
    
    _instance: Optional['ModelRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._models: Dict[str, ModelInfo] = {}
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="model_loader")
        self._loading_futures: Dict[str, Any] = {}
        
        # Register all models with their loaders
        self._register_default_models()
        
        logger.info("✅ ModelRegistry initialized")
    
    def _register_default_models(self):
        """Register all models managed by the registry"""
        # Embeddings model (Critical for RAG)
        self._models["embeddings"] = ModelInfo(name="SentenceTransformer:all-MiniLM-L6-v2")
        
        # Whisper model (STT)
        self._models["whisper"] = ModelInfo(name="Whisper:small")
        
        # Google Speech clients (optional)
        self._models["google_speech"] = ModelInfo(name="GoogleCloudSpeech")
        self._models["google_tts"] = ModelInfo(name="GoogleCloudTTS")
        
        # IndicTrans2 (lazy loaded on demand)
        self._models["indictrans2"] = ModelInfo(name="IndicTrans2:1B")

    def get_status(self, model_name: str) -> ModelStatus:
        """Get the current status of a model"""
        if model_name not in self._models:
            return ModelStatus.NOT_STARTED
        return self._models[model_name].status

    def is_ready(self, model_name: str) -> bool:
        """Check if a model is ready for use"""
        return self.get_status(model_name) == ModelStatus.READY

    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a loaded model instance (returns None if not ready)"""
        if model_name not in self._models:
            return None
        info = self._models[model_name]
        if info.status == ModelStatus.READY:
            return info.model
        return None

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered models"""
        result = {}
        for name, info in self._models.items():
            result[name] = {
                "status": info.status.value,
                "error": info.error,
                "load_time_ms": info.load_time_ms
            }
        return result

    def is_all_ready(self) -> bool:
        """Check if all critical models are ready"""
        # Define critical models that must be ready
        # If model is FAILED or DISABLED, we still allow 'ready' status for the system
        # but NOT_STARTED or LOADING will block readiness
        critical = ["embeddings", "whisper", "indictrans2"] 
        return all(self.is_ready(m) or self.get_status(m) in [ModelStatus.FAILED, ModelStatus.DISABLED] for m in critical)

    def start_background_loading(self):
        """Start loading all models in background threads"""
        logger.info("🚀 Starting background model loading...")
        
        # Load Embeddings
        self._load_in_background("embeddings", self._load_embeddings_model)

        # Load Whisper model
        self._load_in_background("whisper", self._load_whisper_model)
        
        # Load IndicTrans2 (now also in background)
        def _sync_load_indictrans():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Ensure it uses the global service instance
                from app.indictrans2_service import indictrans2_service
                return loop.run_until_complete(indictrans2_service.load_model("en-indic"))
            except Exception as e:
                logger.error(f"IndicTrans2 background load error: {e}")
                return None
        
        self._load_in_background("indictrans2", _sync_load_indictrans)

        # Load Google Speech (optional, may fail silently)
        self._load_in_background("google_speech", self._load_google_speech)
        self._load_in_background("google_tts", self._load_google_tts)
        
        logger.info("📋 Background loading started for: embeddings, whisper, indictrans2, google_speech, google_tts")
    
    def _load_in_background(self, model_name: str, loader_func: Callable):
        """Submit a model loading task to the thread pool"""
        if model_name not in self._models:
            return
            
        info = self._models[model_name]
        if info.status in [ModelStatus.LOADING, ModelStatus.READY]:
            return
        
        info.status = ModelStatus.LOADING
        info.started_at = time.time()
        
        future = self._executor.submit(self._safe_load_wrapper, model_name, loader_func)
        self._loading_futures[model_name] = future
    
    def _safe_load_wrapper(self, model_name: str, loader_func: Callable):
        """Wrapper that catches all exceptions during model loading"""
        info = self._models[model_name]
        start_time = time.time()
        
        try:
            model = loader_func()
            elapsed = (time.time() - start_time) * 1000
            
            # If loader_func returns True (like for indictrans singleton), we don't store True as the model
            if model_name == "indictrans2" and model is True:
                from app.indictrans2_service import indictrans2_service
                info.model = indictrans2_service
            else:
                info.model = model
                
            info.status = ModelStatus.READY
            info.load_time_ms = elapsed
            info.error = None
            
            logger.info(f"✅ [{model_name}] loaded successfully in {elapsed:.0f}ms")
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            info.status = ModelStatus.FAILED
            info.error = str(e)
            info.load_time_ms = elapsed
            
            logger.error(f"❌ [{model_name}] failed to load: {e}")
    
    def _load_embeddings_model(self):
        """Load SentenceTransformer embeddings model"""
        try:
            from sentence_transformers import SentenceTransformer
            # Using a small, efficient model for CPU compatibility
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model
        except ImportError:
            logger.warning("⚠️ sentence_transformers not installed")
            return None
        except Exception as e:
            logger.error(f"Embeddings loading error: {e}")
            return None

    # ==================== Model Loaders ====================
    
    def _load_whisper_model(self):
        """Load Whisper STT model"""
        try:
            import whisper
            # Use 'base' instead of 'small' to prevent CUDA/CPU out of memory meta tensor issues
            model = whisper.load_model("base")
            return model
        except ImportError:
            logger.warning("⚠️ whisper not installed")
            return None
        except Exception as e:
            logger.error(f"Whisper loading error: {e}")
            return None
    
    def _load_google_speech(self):
        """Load Google Cloud Speech client (optional)"""
        try:
            from google.cloud import speech_v1 as speech
            client = speech.SpeechClient()
            return client
        except ImportError:
            logger.info("ℹ️ Google Cloud Speech not available (library not installed)")
            self._models["google_speech"].status = ModelStatus.DISABLED
            return None
        except Exception as e:
            # Google credentials not configured - this is expected and OK
            logger.info(f"ℹ️ Google Speech skipped (credentials not configured): {type(e).__name__}")
            self._models["google_speech"].status = ModelStatus.DISABLED
            return None
    
    def _load_google_tts(self):
        """Load Google Cloud TTS client (optional)"""
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            return client
        except ImportError:
            logger.info("ℹ️ Google Cloud TTS not available (library not installed)")
            self._models["google_tts"].status = ModelStatus.DISABLED
            return None
        except Exception as e:
            logger.info(f"ℹ️ Google TTS skipped (credentials not configured): {type(e).__name__}")
            self._models["google_tts"].status = ModelStatus.DISABLED
            return None
    
    async def load_indictrans2_on_demand(self, direction: str = "en-indic"):
        """Load IndicTrans2 on first use (lazy loading)"""
        if self.is_ready("indictrans2"):
            return self.get_model("indictrans2")
        
        if self._models["indictrans2"].status == ModelStatus.LOADING:
            # Wait for loading to complete
            for _ in range(60):  # Max 60 seconds wait
                await asyncio.sleep(1)
                if self._models["indictrans2"].status != ModelStatus.LOADING:
                    break
            return self.get_model("indictrans2")
        
        # Start loading in background
        info = self._models["indictrans2"]
        info.status = ModelStatus.LOADING
        
        try:
            from app.indictrans2_service import indictrans2_service
            await indictrans2_service.load_model(direction)
            
            info.model = indictrans2_service
            info.status = ModelStatus.READY
            logger.info("✅ IndicTrans2 loaded on demand")
            return indictrans2_service
            
        except Exception as e:
            info.status = ModelStatus.FAILED
            info.error = str(e)
            logger.error(f"❌ IndicTrans2 loading failed: {e}")
            return None
    
    def cleanup(self):
        """Cleanup all models and shutdown executor"""
        logger.info("🧹 Cleaning up ModelRegistry...")
        
        # Clear all models
        for name, info in self._models.items():
            if info.model is not None:
                try:
                    # Try to call cleanup if available
                    if hasattr(info.model, 'cleanup'):
                        info.model.cleanup()
                    del info.model
                except Exception:
                    pass
                info.model = None
                info.status = ModelStatus.NOT_STARTED
        
        # Shutdown executor
        self._executor.shutdown(wait=False)
        
        logger.info("✅ ModelRegistry cleanup complete")


# Global singleton instance
model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    """Get the global model registry instance"""
    return model_registry

