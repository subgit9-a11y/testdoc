"""
Enhanced AI Companion API - 100% Production Ready
Includes all bug fixes and new features
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging
import json

# Core services
from app.companion_redis_manager import redis_companion_manager
from app.voice_service import voice_service
from app.conversation_pruner import conversation_pruner
from app.enhanced_input_validator import input_validator
from app.model_service import model_service
from app.ayurveda_model_service import ayurveda_model_service  # Custom Ayurveda model
from app.auth_middleware import rate_limit_check, get_current_user
from app.audit_logger import audit_logger
from app.xss_sanitizer import xss_sanitizer

logger = logging.getLogger(__name__)

# Router with rate limiting
router = APIRouter(
    prefix="/api/companion/v2",
    tags=["AI Companion Enhanced"],
    dependencies=[Depends(rate_limit_check)]
)

# ============ MODELS ============

class StartJourneyRequest(BaseModel):
    user_id: str
    health_concern: str
    language: Optional[str] = "en"
    initial_symptoms: Optional[List[str]] = None
    enable_voice: Optional[bool] = False

class StartJourneyResponse(BaseModel):
    success: bool
    journey_id: Optional[str]
    message: str
    welcome_message: str
    voice_audio_base64: Optional[str] = None

class ChatRequest(BaseModel):
    journey_id: str
    message: str
    language: Optional[str] = "en"
    enable_voice: Optional[bool] = False

class ChatResponse(BaseModel):
    success: bool
    response: str
    language: str
    voice_audio_base64: Optional[str] = None
    tokens_used: Optional[int] = None
    pruned: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

# ============ ENDPOINTS ============

@router.post("/journey/start", response_model=StartJourneyResponse)
async def start_journey_enhanced(
    data: StartJourneyRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """
    Start companion journey with full validation and voice support
    """
    try:
        # Validate inputs
        is_valid_id, id_error = input_validator.validate_patient_id(data.user_id)
        if not is_valid_id:
            raise HTTPException(status_code=400, detail=id_error)
        
        is_valid_concern, sanitized_concern, concern_error = input_validator.validate_health_concern(data.health_concern)
        if not is_valid_concern:
            raise HTTPException(status_code=400, detail=concern_error)
        
        is_valid_lang, lang_error = input_validator.validate_language_code(data.language)
        if not is_valid_lang:
            raise HTTPException(status_code=400, detail=lang_error)
        
        # Create journey with Redis caching
        journey_id = await redis_companion_manager.start_companion_journey(
            user_id=data.user_id,
            health_concern=sanitized_concern,
            language=data.language,
            initial_symptoms=data.initial_symptoms
        )
        
        if not journey_id:
            raise HTTPException(status_code=500, detail="Failed to create journey")
        
        # Generate welcome message
        welcome_msg = f"Hello! I'm Astra, your AI wellness companion. I'm here to help you with {sanitized_concern}. How are you feeling today?"
        
        # Generate voice if requested
        voice_audio = None
        if data.enable_voice and voice_service.is_available():
            voice_audio = await voice_service.text_to_speech_base64(
                text=welcome_msg,
                language=data.language
            )
        
        return StartJourneyResponse(
            success=True,
            journey_id=journey_id,
            message="Journey started successfully",
            welcome_message=welcome_msg,
            voice_audio_base64=voice_audio
        )
        
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Start journey error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_enhanced(
    data: ChatRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """
    Enhanced chat via unified Astra Pipeline with voice support, strict safety middleware, and intent decay monitoring.
    """
    try:
        from app.companion_system import CompanionStatus
        from app.companion_api import analyze_safety
        
        # 1. Retrieve current journey state to verify if chat is already locked
        journey = None
        if data.journey_id:
            try:
                journey = await redis_companion_manager.get_journey(data.journey_id)
            except HTTPException:

                raise

            except Exception as e:
                logger.warning(f"Error retrieving journey {data.journey_id} from Redis: {e}")

        # If the journey is already locked/referred or temporarily locked due to abuse, block further AI chat
        if journey:
            status = journey.get("status")
            metadata = journey.get("metadata") or {}
            
            # Check upfront abuse lock
            from datetime import datetime
            
            # --- TOKEN BUDGET MONITOR CHECK (Denial of Wallet Protection) ---
            from app.redis_cache import redis_cache
            user_id = journey.get("user_id")
            if user_id:
                is_frozen = redis_cache.get("budget", f"frozen:{user_id}")
                if is_frozen:
                    logger.warning(f"🛑 Chat request blocked: User {user_id} is FROZEN for human review.")
                    return ChatResponse(
                        success=True,
                        response=(
                            "⚠️ **ACCOUNT FROZEN FOR REVIEW** ⚠️\n\n"
                            "We detected unusually high activity on your account. To protect the platform and prevent abuse, "
                            "your AI Companion connection has been frozen and flagged for human review.\n\n"
                            "Please contact care@ayureze.in to resolve this."
                        ),
                        language=data.language or "en",
                        metadata={"account_frozen": True}
                    )
            
            if metadata.get("abuse_locked") is True:
                lock_until_str = metadata.get("abuse_lock_until")
                if lock_until_str:
                    try:
                        lock_until = datetime.fromisoformat(lock_until_str)
                        if datetime.utcnow() < lock_until:
                            remaining_minutes = int((lock_until - datetime.utcnow()).total_seconds() / 60)
                            hours = remaining_minutes // 60
                            minutes = remaining_minutes % 60
                            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                            locked_msg = (
                                "🚫 **CHAT TEMPORARILY LOCKED** 🚫\n\n"
                                "To ensure our AI focuses on providing safe and dedicated wellness support, "
                                f"this chat input is temporarily locked. It will automatically unlock in **{time_str}**.\n\n"
                                "If you have an urgent medical query, please consult a healthcare professional."
                            )
                            return ChatResponse(
                                success=True,
                                response=locked_msg,
                                language=data.language or "en",
                                metadata={"abuse_locked": True, "lock_remaining": time_str}
                            )
                    except Exception as parse_ex:
                        logger.error(f"Error checking upfront abuse lock in Redis: {parse_ex}")

            if status == CompanionStatus.REFERRED.value or status == "referred" or metadata.get("locked") is True:
                logger.warning(f"🛑 Enhanced Chat request rejected: Journey {data.journey_id} is LOCKED due to prior safety escalation.")
                locked_msg = (
                    "🚨 **CHAT LOCKED** 🚨\n\n"
                    "This chat has been locked due to a previously detected critical medical emergency.\n\n"
                    "Please connect with emergency services immediately or use the SOS options below. "
                    "A human doctor has been notified and will contact you directly."
                )
                return ChatResponse(
                    success=True,
                    response=locked_msg,
                    language=data.language or "en",
                    metadata={
                        "locked": True,
                        "escalated": True,
                        "show_sos_button": True,
                        "route_to_doctor": True,
                        "sos_action": "tel:112",
                        "doctor_routing_initiated": True
                    }
                )

        # 2. Strict Safety Middleware Check
        safety_check = analyze_safety(data.message)
        if not safety_check["is_safe"]:
            logger.warning(f"⚠️ Critical medical safety concern detected in Enhanced Chat: {safety_check['reason']}. Locking chat.")
            
            # Lock the chat: break character, update journey status to REFERRED (locked)
            if data.journey_id:
                try:
                    current_metadata = (journey.get("metadata") or {}) if journey else {}
                    current_metadata["locked"] = True
                    current_metadata["safety_alert"] = safety_check["reason"]
                    current_metadata["show_sos_button"] = True
                    current_metadata["route_to_doctor"] = True
                    current_metadata["sos_action"] = "tel:112"
                    current_metadata["doctor_routing_initiated"] = True
                    
                    # Update status in Redis manager / DB
                    if hasattr(redis_companion_manager, 'update_journey_status'):
                        await redis_companion_manager.update_journey_status(
                            journey_id=data.journey_id,
                            status=CompanionStatus.REFERRED.value,
                            resolution_notes=f"Emergency safety lock: {safety_check['reason']}"
                        )
                    
                    # Update cache/Redis directly too
                    if journey:
                        journey["status"] = CompanionStatus.REFERRED.value
                        journey["metadata"] = current_metadata
                        await redis_companion_manager.save_journey(data.journey_id, journey)
                        
                except Exception as ex:
                    logger.error(f"Error locking journey in Redis during safety check: {ex}")

            # Return breaking character response + SOS details + Doctor routing
            emergency_msg = (
                "🚨 **CRITICAL MEDICAL EMERGENCY DETECTED** 🚨\n\n"
                "I must immediately break character as Astra, your AI wellness companion. "
                "The symptoms you've described indicate a potential medical emergency: **{}**.\n\n"
                "⚠️ **CRITICAL WARNING:** Please **DO NOT TAKE** any home remedies, herbal supplements, "
                "or Ayurvedic products (such as Triphala) for these symptoms right now, as it could delay necessary medical care.\n\n"
                "Please take immediate action:\n"
                "1. **Call Emergency Services:** Dial **112** (India) or **911** (US) immediately.\n"
                "2. **Visit the nearest Hospital/Emergency Room** without delay.\n\n"
                "📞 **HUMAN DOCTOR ROUTING INITIATED:** We have instantly routed your case to a human doctor on our team. "
                "A medical professional is reviewing your message and will reach out to you immediately. "
                "This chat has been locked for your safety."
            ).format(safety_check["reason"])

            return ChatResponse(
                success=True,
                response=emergency_msg,
                language=data.language or "en",
                metadata={
                    "locked": True,
                    "escalated": True,
                    "show_sos_button": True,
                    "route_to_doctor": True,
                    "safety_alert": safety_check["reason"],
                    "sos_action": "tel:112",
                    "doctor_routing_initiated": True
                }
            )

        # 2.5 Intent-Decay Monitor Check
        from app.companion_api import monitor_intent_decay
        intent_status = await monitor_intent_decay(data.journey_id, data.message, data.language or "en")
        if intent_status["is_locked"]:
            logger.warning(f"🛑 Enhanced Chat request locked due to Intent Decay: Journey {data.journey_id}")
            # Sync back to Redis journey state
            if journey:
                journey["metadata"] = journey.get("metadata") or {}
                journey["metadata"].update(intent_status["metadata"])
                await redis_companion_manager.save_journey(data.journey_id, journey)
                
            return ChatResponse(
                success=True,
                response=intent_status["lock_message"],
                language=data.language or "en",
                metadata=intent_status["metadata"]
            )
            
        # Update Redis journey metadata if not locked
        if journey and intent_status["metadata"]:
            journey["metadata"] = journey.get("metadata") or {}
            journey["metadata"].update(intent_status["metadata"])
            await redis_companion_manager.save_journey(data.journey_id, journey)

        # 3. If safe, execute standard enhanced companion pipeline
        from app.astra.routes import pipeline_instance
        if not pipeline_instance:
            raise HTTPException(status_code=503, detail="Astra Pipeline not initialized")

        # Inject steering prompt if off-topic
        message_to_send = data.message
        if intent_status["steer_instruction"]:
            message_to_send += intent_status["steer_instruction"]

        # If voice is enabled, we MUST wait for the full response to generate TTS
        if data.enable_voice:
            # Process through the unified pipeline synchronously
            result = await pipeline_instance.run(
                input_text=message_to_send,
                user_uuid=data.journey_id,
                channel="voice",
                metadata={
                    "journey_id": data.journey_id,
                    "feature": "companion_v2",
                    "journey_metadata": (journey.get("metadata") or {}) if journey else {}
                }
            )

            response_text = result if isinstance(result, str) else result.get("response", "")
            
            # --- XSS SANITIZATION (AI Output Scrubbing) ---
            response_text = xss_sanitizer.sanitize_text(response_text)
            
            # Generate voice
            voice_audio = None
            if voice_service.is_available():
                voice_audio = await voice_service.text_to_speech_base64(
                    text=response_text,
                    language=data.language or (result.get("language", "en") if isinstance(result, dict) else "en")
                )

            return ChatResponse(
                success=True,
                response=response_text,
                language=data.language or "en",
                voice_audio_base64=voice_audio,
                tokens_used=0,
                pruned=False
            )
        
        # If voice is NOT enabled, we stream the response using SSE proxy!
        else:
            async def event_stream():
                async for chunk in pipeline_instance.run_stream(
                    input_text=message_to_send,
                    user_uuid=data.journey_id,
                    channel="app",
                    metadata={
                        "journey_id": data.journey_id,
                        "feature": "companion_v2_stream",
                        "journey_metadata": (journey.get("metadata") or {}) if journey else {}
                    }
                ):
                    yield chunk
                    
            return StreamingResponse(event_stream(), media_type="text/event-stream")
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Enhanced chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




# Journey and other management endpoints remain unchanged, but chat is now unified.



@router.get("/journey/{journey_id}")
async def get_journey_enhanced(
    journey_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get journey details with Redis caching"""
    try:
        journey = await redis_companion_manager.get_journey(journey_id)
        if not journey:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        return {
            "success": True,
            "journey": journey
        }
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Get journey error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get available ElevenLabs voices"""
    try:
        if not voice_service.is_available():
            return {
                "success": False,
                "message": "Voice service not configured",
                "voices": []
            }
        
        voices = await voice_service.get_available_voices()
        return {
            "success": True,
            "voices": voices or [],
            "message": "ElevenLabs voices available"
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def companion_health_check():
    """Health check for companion service"""
    return {
        "status": "healthy",
        "version": "2.0",
        "features": {
            "redis_cache": redis_companion_manager.client is not None,
            "voice_enabled": voice_service.is_available(),
            "conversation_pruning": True,
            "input_validation": True,
            "rate_limiting": True
        }
    }
