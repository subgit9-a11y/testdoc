"""
Astra Model Inference - Unified AI Response Generation
Uses AstraBrainClient to connect to Astra Companion for all AI operations
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AstraModelInference:
    """
    Wrapper for AI model inference using Astra Companion
    All AI responses flow through the AstraBrainClient
    """
    
    def __init__(self):
        self._brain_client = None
        self.loaded = False

    @property
    def brain(self):
        """Lazy load the brain client"""
        if self._brain_client is None:
            from app.astra_brain_client import get_brain_client
            self._brain_client = get_brain_client()
        return self._brain_client

    async def load_model(self):
        """
        Check connection to Astra Brain API
        """
        try:
            result = await self.brain.check_health()
            self.loaded = result.get("status") == "online"
            
            if self.loaded:
                logger.info("✅ AstraModelInference connected to Companion Engine")
            else:
                logger.warning("⚠️ AstraModelInference: Brain API not responding")
        except Exception as e:
            logger.error(f"❌ AstraModelInference connection failed: {e}")
            self.loaded = False

    def is_loaded(self) -> bool:
        return self.loaded

    async def generate_response(
        self, 
        prompt: str, 
        language: str = "en", 
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate AI response using Astra Companion v1/chat
        
        Args:
            prompt: User's question or message
            language: Response language (en, hi, ta)
            context: Optional additional context
            **kwargs: Additional params (ignored for API compatibility)
        
        Returns:
            AI-generated response string
        """
        try:
            # Add context to prompt if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            # Call the brain API
            result = await self.brain.chat(query=full_prompt, language=language)
            
            if result.success:
                logger.info(f"✅ Response generated ({result.mode}): {len(result.answer)} chars")
                return result.answer
            else:
                logger.warning("Brain API returned unsuccessful, using fallback")
                return self._get_fallback_response(prompt, language)
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._get_fallback_response(prompt, language)
    
    def _get_fallback_response(self, prompt: str, language: str) -> str:
        """Fallback response when AI is unavailable"""
        fallbacks = {
            "en": "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment, or consult with an Ayurvedic practitioner for immediate guidance.",
            "hi": "क्षमा करें, मुझे अभी अपने ज्ञान आधार से कनेक्ट करने में समस्या हो रही है। कृपया कुछ देर बाद पुनः प्रयास करें।",
            "ta": "மன்னிக்கவும், எனது அறிவுத் தளத்துடன் இணைப்பதில் சிக்கல் உள்ளது. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."
        }
        return fallbacks.get(language, fallbacks["en"])

    def cleanup(self):
        """Cleanup resources"""
        self._brain_client = None
        self.loaded = False
        logger.info("AstraModelInference shutdown complete")

