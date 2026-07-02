"""
Astra Voice Service - Open Source Text-to-Speech Integration

PROVIDERS (in order of preference):
1. edge-tts - FREE Microsoft Edge neural voices (no API key needed!)
2. gTTS - FREE Google TTS (basic quality)
3. pyttsx3 - Offline system TTS
4. ElevenLabs - Premium (requires API key)

FEATURES:
- Multi-language support (English, Hindi, Tamil, Telugu, etc.)
- High-quality neural voices via edge-tts
- No API keys required for basic operation
- Async support
"""

import os
import logging
import asyncio
import tempfile
import base64
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Check available TTS providers
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.info("ℹ️ edge-tts not installed")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.info("ℹ️ gTTS not installed")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.info("ℹ️ pyttsx3 not installed")

try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_AVAILABLE = True
    # Only set API key if available
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        set_api_key(api_key)
except ImportError:
    ELEVENLABS_AVAILABLE = False


class VoiceService:
    """
    Multi-provider voice service with open-source TTS support.
    
    Uses edge-tts by default (free Microsoft neural voices).
    """
    
    # Edge TTS voice mapping for Indian languages
    EDGE_VOICES = {
        "en": "en-IN-NeerjaNeural",      # Indian English Female
        "en-IN": "en-IN-NeerjaNeural",
        "en-US": "en-US-JennyNeural",
        "hi": "hi-IN-SwaraNeural",        # Hindi Female
        "hi-IN": "hi-IN-SwaraNeural",
        "ta": "ta-IN-PallaviNeural",      # Tamil Female
        "ta-IN": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",       # Telugu Female
        "te-IN": "te-IN-ShrutiNeural",
        "kn": "kn-IN-SapnaNeural",        # Kannada Female
        "kn-IN": "kn-IN-SapnaNeural",
        "ml": "ml-IN-SobhanaNeural",      # Malayalam Female
        "ml-IN": "ml-IN-SobhanaNeural",
        "mr": "mr-IN-AarohiNeural",       # Marathi Female
        "mr-IN": "mr-IN-AarohiNeural",
        "bn": "bn-IN-TanishaaNeural",     # Bengali Female
        "bn-IN": "bn-IN-TanishaaNeural",
        "gu": "gu-IN-DhwaniNeural",       # Gujarati Female
        "gu-IN": "gu-IN-DhwaniNeural",
    }
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.default_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.timeout = 30.0
        
        # Log available providers
        providers = []
        if EDGE_TTS_AVAILABLE:
            providers.append("edge-tts (FREE)")
        if GTTS_AVAILABLE:
            providers.append("gTTS (FREE)")
        if PYTTSX3_AVAILABLE:
            providers.append("pyttsx3 (offline)")
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            providers.append("ElevenLabs (premium)")
        
        if providers:
            logger.info(f"✅ Voice Service initialized with: {', '.join(providers)}")
        else:
            logger.warning("⚠️ No TTS providers available!")
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en"
    ) -> Optional[bytes]:
        """
        Convert text to speech using the best available provider.
        
        Priority: edge-tts -> gTTS -> ElevenLabs -> pyttsx3
        
        Args:
            text: Text to convert
            voice_id: Optional voice ID (for ElevenLabs)
            language: Language code (en, hi, ta, etc.)
        
        Returns:
            Audio bytes (MP3 format) or None if failed
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided to TTS")
            return None
        
        # Limit text length
        if len(text) > 5000:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 5000")
            text = text[:5000]
        
        # Try edge-tts first (best quality, free)
        if EDGE_TTS_AVAILABLE:
            try:
                audio = await self._edge_tts(text, language)
                if audio:
                    return audio
            except Exception as e:
                logger.warning(f"edge-tts failed: {e}")
        
        # Try gTTS (free, requires internet)
        if GTTS_AVAILABLE:
            try:
                audio = await self._gtts(text, language)
                if audio:
                    return audio
            except Exception as e:
                logger.warning(f"gTTS failed: {e}")
        
        # Try ElevenLabs if API key is available
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            try:
                audio = await self._elevenlabs_tts(text, voice_id)
                if audio:
                    return audio
            except Exception as e:
                logger.warning(f"ElevenLabs failed: {e}")
        
        # Fallback to pyttsx3 (offline)
        if PYTTSX3_AVAILABLE:
            try:
                audio = await self._pyttsx3(text)
                if audio:
                    return audio
            except Exception as e:
                logger.warning(f"pyttsx3 failed: {e}")
        
        logger.error("All TTS providers failed!")
        return None
    
    async def _edge_tts(self, text: str, language: str) -> Optional[bytes]:
        """Generate speech using edge-tts (Microsoft neural voices)"""
        voice = self.EDGE_VOICES.get(language, "en-IN-NeerjaNeural")
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
            
            # Read the audio file
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(f"✅ edge-tts: Generated {len(audio_data)} bytes with voice {voice}")
            return audio_data
            
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _gtts(self, text: str, language: str) -> Optional[bytes]:
        """Generate speech using Google TTS (free)"""
        # Map language codes
        gtts_lang = language.split("-")[0]  # "en-IN" -> "en"
        
        def _generate():
            tts = gTTS(text=text, lang=gtts_lang)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tts.save(tmp.name)
                return tmp.name
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        tmp_path = await loop.run_in_executor(None, _generate)
        
        try:
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(f"✅ gTTS: Generated {len(audio_data)} bytes")
            return audio_data
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _elevenlabs_tts(self, text: str, voice_id: Optional[str]) -> Optional[bytes]:
        """Generate speech using ElevenLabs (premium)"""
        voice_id = voice_id or self.default_voice_id
        
        def _generate():
            return generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2"
            )
        
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(None, _generate)
        
        logger.info(f"✅ ElevenLabs: Generated audio")
        return audio
    
    async def _pyttsx3(self, text: str) -> Optional[bytes]:
        """Generate speech using pyttsx3 (offline)"""
        def _generate():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                engine.save_to_file(text, tmp.name)
                engine.runAndWait()
                return tmp.name
        
        loop = asyncio.get_event_loop()
        tmp_path = await loop.run_in_executor(None, _generate)
        
        try:
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(f"✅ pyttsx3: Generated {len(audio_data)} bytes")
            return audio_data
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def text_to_speech_base64(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Convert text to speech and return as base64 string.
        Useful for API responses.
        """
        audio_bytes = await self.text_to_speech(text, voice_id, language)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('utf-8')
        return None
    
    async def get_available_voices(self, language: str = None) -> Dict[str, Any]:
        """Get list of available voices"""
        voices = {
            "edge_tts": [],
            "elevenlabs": [],
            "available_languages": list(self.EDGE_VOICES.keys())
        }
        
        # Add edge-tts voices
        if EDGE_TTS_AVAILABLE:
            if language:
                voice = self.EDGE_VOICES.get(language)
                if voice:
                    voices["edge_tts"].append({"language": language, "voice": voice})
            else:
                for lang, voice in self.EDGE_VOICES.items():
                    voices["edge_tts"].append({"language": lang, "voice": voice})
        
        return voices
    
    def is_available(self) -> bool:
        """Check if any voice service is available"""
        return EDGE_TTS_AVAILABLE or GTTS_AVAILABLE or PYTTSX3_AVAILABLE or (
            ELEVENLABS_AVAILABLE and bool(self.elevenlabs_api_key)
        )


# Global instance
voice_service = VoiceService()
