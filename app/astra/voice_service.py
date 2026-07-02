"""
Astra Voice Service - Speech-to-Text and Text-to-Speech Integration

ARCHITECTURE:
- Uses model_registry for Whisper STT model (loaded in background)
- Uses edge-tts for TTS (free Microsoft neural voices)
- No API keys required for basic operation
- Graceful fallbacks on all operations

PROVIDERS:
- STT: Whisper (local) or Google Speech (optional)
- TTS: edge-tts (free) -> gTTS (free) -> ElevenLabs (premium)

FEATURES:
- Multi-language support (English, Hindi, Tamil, Telugu, etc.)
- High-quality Indian language voices
- Async support
- No blocking on model loading
"""

import logging
import os
import tempfile
import asyncio
from typing import Optional, Dict, Literal
from pathlib import Path

logger = logging.getLogger(__name__)

# Check available TTS providers
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.info("edge-tts not installed")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_AVAILABLE = True
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        set_api_key(api_key)
except ImportError:
    ELEVENLABS_AVAILABLE = False


class VoiceService:
    """
    Unified voice service for Astra.
    
    Uses:
    - model_registry for Whisper STT (background loaded)
    - edge-tts for TTS (free, no API key)
    """
    
    # Edge TTS voice mapping for Indian languages
    EDGE_VOICES = {
        "en-IN": "en-IN-NeerjaNeural",
        "en-US": "en-US-JennyNeural",
        "hi-IN": "hi-IN-SwaraNeural",
        "ta-IN": "ta-IN-PallaviNeural",
        "te-IN": "te-IN-ShrutiNeural",
        "kn-IN": "kn-IN-SapnaNeural",
        "ml-IN": "ml-IN-SobhanaNeural",
        "mr-IN": "mr-IN-AarohiNeural",
        "bn-IN": "bn-IN-TanishaaNeural",
        "gu-IN": "gu-IN-DhwaniNeural",
    }
    
    def __init__(
        self,
        stt_provider: Literal["google", "whisper"] = "whisper",
        tts_provider: Literal["edge", "google", "elevenlabs"] = "edge",
        default_language: str = "en-IN"
    ):
        """
        Initialize voice service.
        
        Args:
            stt_provider: Speech-to-text provider
            tts_provider: Text-to-speech provider
            default_language: Default language code
        """
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.default_language = default_language
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Log available providers
        providers = []
        if EDGE_TTS_AVAILABLE:
            providers.append("edge-tts")
        if GTTS_AVAILABLE:
            providers.append("gTTS")
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            providers.append("ElevenLabs")
        
        logger.info(f"VoiceService initialized (STT: {stt_provider}, TTS: {providers})")
    
    def _get_whisper_model(self):
        """Get Whisper model from model_registry"""
        from app.model_registry import model_registry
        return model_registry.get_model("whisper")
    
    def _is_whisper_ready(self) -> bool:
        """Check if Whisper is ready"""
        from app.model_registry import model_registry
        return model_registry.is_ready("whisper")
    
    def _get_google_speech_client(self):
        """Get Google Speech client from model_registry"""
        from app.model_registry import model_registry
        return model_registry.get_model("google_speech")
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language_code: Optional[str] = None,
        audio_format: str = "wav"
    ) -> Dict:
        """
        Convert speech to text using Whisper (local).
        
        Args:
            audio_data: Audio file bytes
            language_code: Language code (e.g., 'en-IN', 'hi-IN')
            audio_format: Audio format (wav, mp3, ogg)
        
        Returns:
            {
                "transcript": str,
                "confidence": float,
                "language": str,
                "provider": str
            }
        """
        language_code = language_code or self.default_language
        
        try:
            # Try Whisper first
            if self._is_whisper_ready():
                return await self._whisper_stt(audio_data, language_code)
            
            # Try Google Speech as fallback
            google_client = self._get_google_speech_client()
            if google_client:
                return await self._google_stt(audio_data, language_code, audio_format, google_client)
            
            # No provider available
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": language_code,
                "provider": "none",
                "error": "STT models are still loading. Please try again."
            }
            
        except Exception as e:
            logger.error(f"STT failed: {e}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": language_code,
                "provider": self.stt_provider,
                "error": str(e)
            }
    
    async def text_to_speech(
        self,
        text: str,
        language_code: Optional[str] = None,
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0
    ) -> Dict:
        """
        Convert text to speech using edge-tts (free).
        
        Args:
            text: Text to convert
            language_code: Language code
            voice_name: Specific voice name
            speaking_rate: Speech rate (0.25 to 4.0)
        
        Returns:
            {
                "audio_data": bytes,
                "format": str,
                "language": str,
                "provider": str
            }
        """
        language_code = language_code or self.default_language
        
        if not text or len(text.strip()) == 0:
            return {
                "audio_data": b"",
                "format": "none",
                "language": language_code,
                "provider": "none",
                "error": "Empty text provided"
            }
        
        # Limit text length
        if len(text) > 5000:
            text = text[:5000]
        
        try:
            # Try edge-tts first (free, best quality)
            if EDGE_TTS_AVAILABLE:
                return await self._edge_tts(text, language_code)
            
            # Try gTTS (free, basic)
            if GTTS_AVAILABLE:
                return await self._gtts_tts(text, language_code)
            
            # Try ElevenLabs (premium)
            if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
                return await self._elevenlabs_tts(text, voice_name)
            
            return {
                "audio_data": b"",
                "format": "none",
                "language": language_code,
                "provider": "none",
                "error": "No TTS provider available"
            }
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return {
                "audio_data": b"",
                "format": "none",
                "language": language_code,
                "provider": "edge",
                "error": str(e)
            }
    
    async def _whisper_stt(
        self,
        audio_data: bytes,
        language_code: str
    ) -> Dict:
        """OpenAI Whisper Speech-to-Text"""
        whisper_model = self._get_whisper_model()
        if not whisper_model:
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": language_code,
                "provider": "whisper",
                "error": "Whisper model not loaded yet"
            }
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_path = temp_audio.name
        
        try:
            language = language_code.split('-')[0]
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: whisper_model.transcribe(temp_path, language=language, fp16=False)
            )
            
            transcript = result["text"].strip()
            
            logger.info(f"Whisper STT: '{transcript[:50]}...'")
            
            return {
                "transcript": transcript,
                "confidence": 0.95,
                "language": language_code,
                "provider": "whisper"
            }
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    async def _google_stt(
        self,
        audio_data: bytes,
        language_code: str,
        audio_format: str,
        speech_client
    ) -> Dict:
        """Google Cloud Speech-to-Text"""
        from google.cloud import speech_v1 as speech
        
        if audio_format == "wav":
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif audio_format == "mp3":
            encoding = speech.RecognitionConfig.AudioEncoding.MP3
        else:
            encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
        
        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        audio = speech.RecognitionAudio(content=audio_data)
        response = speech_client.recognize(config=config, audio=audio)
        
        if response.results:
            result = response.results[0]
            transcript = result.alternatives[0].transcript
            confidence = result.alternatives[0].confidence
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": language_code,
                "provider": "google"
            }
        else:
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": language_code,
                "provider": "google",
                "error": "No speech detected"
            }
    
    async def _edge_tts(self, text: str, language_code: str) -> Dict:
        """Generate speech using edge-tts (FREE Microsoft neural voices)"""
        voice = self.EDGE_VOICES.get(language_code, "en-IN-NeerjaNeural")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
            
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(f"edge-tts: Generated {len(audio_data)} bytes with {voice}")
            
            return {
                "audio_data": audio_data,
                "format": "mp3",
                "language": language_code,
                "provider": "edge-tts",
                "voice": voice
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _gtts_tts(self, text: str, language_code: str) -> Dict:
        """Generate speech using gTTS (free)"""
        lang = language_code.split("-")[0]
        
        def _generate():
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tts.save(tmp.name)
                return tmp.name
        
        loop = asyncio.get_event_loop()
        tmp_path = await loop.run_in_executor(None, _generate)
        
        try:
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            return {
                "audio_data": audio_data,
                "format": "mp3",
                "language": language_code,
                "provider": "gtts"
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _elevenlabs_tts(self, text: str, voice_name: Optional[str]) -> Dict:
        """ElevenLabs Text-to-Speech (Premium)"""
        voice_map = {
            "rachel": "21m00Tcm4TlvDq8ikWAM",
            "bella": "EXAVITQu4vr4xnSDxMaL",
            "adam": "pNInz6obpgDQGcFmaJgB",
        }
        
        voice_id = voice_map.get(voice_name.lower() if voice_name else "rachel", voice_map["rachel"])
        
        def _generate():
            return generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
        
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(None, _generate)
        
        return {
            "audio_data": audio,
            "format": "mp3",
            "language": "multi",
            "provider": "elevenlabs",
            "voice": voice_name or "rachel"
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return {
            "en-IN": "English (India)",
            "hi-IN": "Hindi",
            "ta-IN": "Tamil",
            "te-IN": "Telugu",
            "kn-IN": "Kannada",
            "ml-IN": "Malayalam",
            "mr-IN": "Marathi",
            "bn-IN": "Bengali",
            "gu-IN": "Gujarati",
            "en-US": "English (US)"
        }
    
    def is_stt_available(self) -> bool:
        """Check if STT is available"""
        return self._is_whisper_ready() or self._get_google_speech_client() is not None
    
    def is_tts_available(self) -> bool:
        """Check if TTS is available"""
        return EDGE_TTS_AVAILABLE or GTTS_AVAILABLE or (ELEVENLABS_AVAILABLE and bool(self.elevenlabs_api_key))
