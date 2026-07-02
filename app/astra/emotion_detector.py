"""
Astra Emotion Detector - NLP-Based Emotion Detection

This module detects emotions from user input using rule-based NLP.
It does NOT track emotional states over time (forbidden).
It only identifies current emotional tone to adjust response style.

IMPORTANT: This is NOT emotional dependency tracking.
It's purely for language style adjustment.
"""

import logging
import re
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionCategory(Enum):
    """Emotion categories for response tone adjustment"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CURIOUS = "curious"
    GRATEFUL = "grateful"
    CONCERNED = "concerned"
    CONFUSED = "confused"


class EmotionDetector:
    """
    Rule-based emotion detection for tone adjustment.
    
    RULES:
    - Detects current emotional tone only
    - Does NOT track emotional states over time
    - Does NOT make mental health inferences
    - Used ONLY for response style adjustment
    """
    
    def __init__(self):
        self.emotion_patterns = self._compile_emotion_patterns()
        logger.info("✅ Emotion Detector initialized")
    
    def _compile_emotion_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile emotion detection patterns"""
        patterns = {
            EmotionCategory.HAPPY.value: [
                re.compile(r'\b(happy|great|wonderful|excellent|amazing|love|thank you)\b', re.IGNORECASE),
                re.compile(r'😊|😄|😃|🙂|❤️|👍'),
                re.compile(r'\b(feeling good|doing well|much better)\b', re.IGNORECASE),
            ],
            EmotionCategory.ANXIOUS.value: [
                re.compile(r'\b(worried|anxious|nervous|scared|afraid|concerned)\b', re.IGNORECASE),
                re.compile(r'😰|😟|😥|😓'),
                re.compile(r'\b(what if|is it serious|should i worry)\b', re.IGNORECASE),
            ],
            EmotionCategory.FRUSTRATED.value: [
                re.compile(r'\b(frustrated|annoyed|irritated|fed up|tired of)\b', re.IGNORECASE),
                re.compile(r'😤|😠|😡'),
                re.compile(r'\b(not working|doesn\'t help|waste of time)\b', re.IGNORECASE),
            ],
            EmotionCategory.CURIOUS.value: [
                re.compile(r'\b(how|why|what|when|where|tell me|explain|curious)\b', re.IGNORECASE),
                re.compile(r'🤔|🧐'),
                re.compile(r'\b(want to know|interested in|learn about)\b', re.IGNORECASE),
            ],
            EmotionCategory.GRATEFUL.value: [
                re.compile(r'\b(thank|thanks|grateful|appreciate|helpful)\b', re.IGNORECASE),
                re.compile(r'🙏|😊|❤️'),
                re.compile(r'\b(you helped|very helpful|really appreciate)\b', re.IGNORECASE),
            ],
            EmotionCategory.CONCERNED.value: [
                re.compile(r'\b(concerned|worried about|not sure|uncertain)\b', re.IGNORECASE),
                re.compile(r'😕|🤨'),
                re.compile(r'\b(is this normal|should i be|is it okay)\b', re.IGNORECASE),
            ],
            EmotionCategory.CONFUSED.value: [
                re.compile(r'\b(confused|don\'t understand|unclear|not sure what)\b', re.IGNORECASE),
                re.compile(r'😕|🤷'),
                re.compile(r'\b(what does|what do you mean|can you explain)\b', re.IGNORECASE),
            ],
        }
        
        return patterns
    
    def detect(self, text: str) -> str:
        """
        Detect emotion from text.
        
        Args:
            text: User's input text
        
        Returns:
            Emotion category (string)
        """
        # Count matches for each emotion
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches)
            
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return emotion with highest score
        if emotion_scores:
            detected_emotion = max(emotion_scores, key=emotion_scores.get)
            logger.info("🎭 Emotion detected: %s (score: %d)", 
                       detected_emotion, emotion_scores[detected_emotion])
            return detected_emotion
        else:
            logger.info("🎭 Emotion: neutral (no strong indicators)")
            return EmotionCategory.NEUTRAL.value
    
    def get_emotion_intensity(self, text: str, emotion: str) -> float:
        """
        Get intensity of a specific emotion (0.0 to 1.0).
        
        Args:
            text: User's input text
            emotion: Emotion to measure
        
        Returns:
            Intensity score (0.0 to 1.0)
        """
        if emotion not in self.emotion_patterns:
            return 0.0
        
        patterns = self.emotion_patterns[emotion]
        total_matches = 0
        
        for pattern in patterns:
            matches = pattern.findall(text)
            total_matches += len(matches)
        
        # Normalize to 0-1 range (cap at 5 matches = 1.0)
        intensity = min(total_matches / 5.0, 1.0)
        
        return intensity
    
    # =========================================================================
    # AI-Powered Methods (using api.ayureze.in)
    # =========================================================================
    
    async def ai_detect(self, text: str) -> Dict[str, str]:
        """
        Use AI to detect emotion from text.
        Falls back to local detection if AI is unavailable.
        
        Uses api.ayureze.in/v1/detect_emotion
        
        Args:
            text: User's input text
        
        Returns:
            Dict with emotion and intensity
        """
        try:
            from app.astra_brain_client import get_brain_client
            brain = get_brain_client()
            
            result = await brain.detect_emotion(text)
            
            logger.info(f"🎭 AI Emotion: {result.emotion} ({result.intensity})")
            
            return {
                "emotion": result.emotion,
                "intensity": result.intensity,
                "source": "ai"
            }
            
        except Exception as e:
            logger.warning(f"AI emotion detection failed: {e}, using local")
            local_emotion = self.detect(text)
            intensity = self.get_emotion_intensity(text, local_emotion)
            
            return {
                "emotion": local_emotion,
                "intensity": "Medium" if intensity > 0.3 else "Low",
                "source": "local"
            }


# Global instance
emotion_detector = EmotionDetector()

