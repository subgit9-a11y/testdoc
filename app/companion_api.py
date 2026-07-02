"""
AI Wellness Companion API Endpoints
Complete REST API for the AI Wellness Companion system with strict Safety Middleware and Unified Astra Pipeline.
"""

from fastapi import APIRouter, HTTPException, Body, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.companion_system import (
    companion_manager,
    CompanionStatus,
    CaseStatus,
    InterventionType
)
from app.database import db_manager
from app.language_utils import LanguageManager
from app.auth_middleware import rate_limit_check, get_current_user
from app.xss_sanitizer import xss_sanitizer
from app.audit_logger import audit_logger
from app.redis_cache import redis_cache

logger = logging.getLogger(__name__)

# Router with rate limiting applied
router = APIRouter(
    prefix="/api/companion",
    tags=["AI Wellness Companion"],
    dependencies=[Depends(rate_limit_check)]
)

# Initialize language manager
lang_manager = LanguageManager()

# ============ REQUEST/RESPONSE MODELS ============

class StartJourneyRequest(BaseModel):
    user_id: str = Field(..., description="Patient's unique ID")
    health_concern: str = Field(..., description="Main health concern")
    language: Optional[str] = Field("en", description="Preferred language (en/hi/ta)")
    initial_symptoms: Optional[List[str]] = Field(None, description="List of initial symptoms")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")

class StartJourneyResponse(BaseModel):
    success: bool
    journey_id: Optional[str]
    message: str
    welcome_message: str

class ChatRequest(BaseModel):
    journey_id: str = Field(..., description="Companion journey ID")
    message: str = Field(..., description="Patient's message")
    language: Optional[str] = Field("en", description="Message language")

class ChatResponse(BaseModel):
    success: bool
    response: str
    language: str
    detected_language: str
    intervention_type: str
    metadata: Dict[str, Any]

class CreateCaseRequest(BaseModel):
    journey_id: str
    user_id: str
    doctor_id: str
    diagnosis: str
    prescription_id: Optional[str] = None
    diet_plan: Optional[Dict[str, Any]] = None
    treatment_duration_days: int = 30
    follow_up_schedule: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class CreateCaseResponse(BaseModel):
    success: bool
    case_id: Optional[str]
    message: str

class UpdateProgressRequest(BaseModel):
    case_id: str
    progress_percentage: float
    adherence_score: float
    notes: Optional[str] = None

class MilestoneRequest(BaseModel):
    journey_id: str
    milestone_type: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

# ============ SAFETY MIDDLEWARE CORE ============

def analyze_safety(text: str) -> Dict[str, Any]:
    """
    Deterministic safety check to detect critical medical emergencies offline-safe.
    Catches variations of chest pain, breathing issues, severe bleeding, and general crisis conditions.
    """
    import re
    
    emergency_patterns = {
        "chest_pain": [
            r'\bchest\s+(pain|hurts|hurting|tightness|pressure|ache|squeezing)\b',
            r'\bpain\s+in\s+(my\s+)?chest\b',
            r'\bheart\s+hurts\b',
            r'\bheart\s+attack\b',
            r'\bcardiac\s+arrest\b',
            r'\btight\s+chest\b'
        ],
        "breathing_issues": [
            r'\b(can\'t|cannot|unable\s+to|trouble|difficulty)\s+breathe\b',
            r'\bshortness\s+of\s+breath\b',
            r'\bbreathing\s+(issues|problems|difficulty)\b',
            r'\b(breathless|breathlessness|choking|suffocating)\b',
            r'\bgasping\s+for\s+air\b'
        ],
        "severe_bleeding": [
            r'\b(severe|heavy|profuse|excessive|non-stop|unstoppable)\s+bleeding\b',
            r'\bbleeding\s+(heavily|profusely|non-stop)\b',
            r'\bgushing\s+blood\b',
            r'\bhemorrhage\b',
            r'\blost\s+a\s+lot\s+of\s+blood\b'
        ],
        "general_emergencies": [
            r'\b(stroke|seizure|convulsion|unconscious|passed\s+out|loss\s+of\s+consciousness)\b',
            r'\b(suicidal|self\s*-?\s*harm|kill\s+myself|end\w*\s+my\s+life|ending\s+my\s+life)\b'
        ]
    }
    
    for category, patterns in emergency_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                category_names = {
                    "chest_pain": "Critical Chest Pain/Heart Concern",
                    "breathing_issues": "Acute Breathing/Respiratory Issues",
                    "severe_bleeding": "Severe Uncontrolled Bleeding",
                    "general_emergencies": "Critical General Emergency"
                }
                return {
                    "is_safe": False,
                    "reason": category_names.get(category, "Critical Medical Emergency"),
                    "category": category
                }
                
    return {"is_safe": True, "reason": None, "category": None}


async def save_journey_metadata(journey_id: str, journey: dict, metadata: dict):
    """Utility to persist metadata across memory caches and databases safely."""
    try:
        # Update local companion cache
        from app.companion_cache import companion_cache
        cached_journey = companion_cache.get_journey(journey_id)
        if cached_journey:
            cached_journey["metadata"] = metadata
            companion_cache.set_journey(journey_id, cached_journey)
        
        # Update journey dictionary in-place
        journey["metadata"] = metadata

        # Update in database if Supabase is connected
        if companion_manager.client:
            try:
                companion_manager.client.table("companion_journeys").update({
                    "metadata": metadata
                }).eq("id", journey_id).execute()
            except Exception as db_ex:
                logger.warning(f"Failed to persist intent metadata to Supabase: {db_ex}")
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error saving journey metadata: {e}")


async def monitor_intent_decay(journey_id: str, message: str, language: str) -> Dict[str, Any]:
    """
    Tracks non-healthcare intents consecutively.
    If consecutive off-topic queries reach 3, triggers a temporary 4-hour lock.
    Returns a dict with state information:
      - is_locked: bool
      - lock_message: str (if locked)
      - steer_instruction: str (system steering prompt)
      - metadata: dict of updated state keys
    """
    from datetime import datetime, timedelta
    
    # 1. Retrieve journey
    journey = None
    if journey_id:
        try:
            journey = await companion_manager.get_journey(journey_id)
        except HTTPException:

            raise

        except Exception as e:
            logger.warning(f"Error retrieving journey {journey_id} for intent monitoring: {e}")

    if not journey:
        return {
            "is_locked": False,
            "lock_message": None,
            "steer_instruction": "",
            "metadata": {}
        }

    metadata = journey.get("metadata") or {}

    # 2. Check if already locked by abuse
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
                    return {
                        "is_locked": True,
                        "lock_message": (
                            "🚫 **CHAT TEMPORARILY LOCKED** 🚫\n\n"
                            "To ensure our AI focuses on providing safe and dedicated wellness support, "
                            f"this chat input is temporarily locked. It will automatically unlock in **{time_str}**.\n\n"
                            "If you have an urgent medical query, please consult a healthcare professional."
                        ),
                        "steer_instruction": "",
                        "metadata": {"abuse_locked": True, "lock_remaining": time_str}
                    }
                else:
                    # Lock expired! Reset counters
                    metadata["abuse_locked"] = False
                    metadata["abuse_lock_until"] = None
                    metadata["non_healthcare_consecutive_count"] = 0
            except HTTPException:

                raise

            except Exception as e:
                logger.error(f"Error parsing lock time: {e}")

    # 3. Analyze intent
    is_healthcare = lang_manager.is_ayurveda_related(message, language)
    consecutive_count = metadata.get("non_healthcare_consecutive_count", 0)

    if not is_healthcare:
        consecutive_count += 1
    else:
        consecutive_count = 0  # Reset on any on-topic query

    metadata["non_healthcare_consecutive_count"] = consecutive_count

    # 4. Handle consecutive off-topic limits
    if consecutive_count >= 3:
        # Lock session for 4 hours
        lock_until = datetime.utcnow() + timedelta(hours=4)
        metadata["abuse_locked"] = True
        metadata["abuse_lock_until"] = lock_until.isoformat()
        
        # Save state changes back to DB/Cache
        await save_journey_metadata(journey_id, journey, metadata)

        lock_msg = (
            "🌸 *I'm glad we could chat! I'll be here if you need any medical assistance. Have a great day!* 🌸\n\n"
            "⚠️ **System Note:** Chat input is temporarily locked for 4 hours to help stay focused on wellness guidance."
        )
        return {
            "is_locked": True,
            "lock_message": lock_msg,
            "steer_instruction": "",
            "metadata": {
                "abuse_locked": True,
                "lock_remaining": "4h 0m",
                "non_healthcare_consecutive_count": consecutive_count
            }
        }

    # 5. Steer conversation if 1 or 2 off-topic queries
    steer_instruction = ""
    if consecutive_count > 0:
        steer_instruction = (
            "\n[SYSTEM NOTICE: The user's query is unrelated to health, medicine, or Ayurveda. "
            "Gently and warmly pivot the response back to their wellness journey or Ayurveda.]"
        )

    # Save state changes back to DB/Cache
    await save_journey_metadata(journey_id, journey, metadata)

    return {
        "is_locked": False,
        "lock_message": None,
        "steer_instruction": steer_instruction,
        "metadata": {
            "abuse_locked": False,
            "non_healthcare_consecutive_count": consecutive_count
        }
    }


# ============ COMPANION JOURNEY ENDPOINTS ============

@router.post("/journey/start", response_model=StartJourneyResponse)
async def start_companion_journey(
    request: StartJourneyRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """
    Start a new AI Wellness Companion journey
    """
    try:
        # Create companion journey
        journey_id = await companion_manager.start_companion_journey(
            user_id=request.user_id,
            health_concern=request.health_concern,
            language=request.language,
            initial_symptoms=request.initial_symptoms,
            metadata=request.metadata
        )
        
        if not journey_id:
            raise HTTPException(status_code=500, detail="Failed to start companion journey")
        
        # Create Supabase chat session
        session_id = None
        try:
            session_id = await db_manager.create_chat_session(
                user_id=request.user_id,
                language=request.language
            )
        except HTTPException:

            raise

        except Exception as e:
            logger.warning(f"Could not create chat session (continuing anyway): {e}")
        
        # Generate welcome message using the model service if available
        welcome_prompt = f"Welcome a new patient starting their wellness journey for {request.health_concern}. Introduce yourself as Astra, their AI Wellness Companion, and ask how they're feeling."
        
        try:
            from app.model_service import model_service
            welcome_message = await model_service.generate_response(
                prompt=welcome_prompt,
                language=request.language,
                context=f"Health concern: {request.health_concern}",
                max_length=300
            )
        except Exception as ex:
            logger.warning(f"Failed to generate response using model_service: {ex}")
            welcome_message = f"Welcome! I'm Astra, your AI Wellness Companion. I'm here to support you with your health concern ({request.health_concern}). How are you feeling today?"
        
        # Save welcome message
        if session_id:
            try:
                await db_manager.save_chat_message(
                    session_id=session_id,
                    user_message=f"Starting journey for {request.health_concern}",
                    assistant_response=welcome_message,
                    language=request.language or "en",
                    metadata={"journey_id": journey_id, "type": "welcome"}
                )
            except HTTPException:

                raise

            except Exception as e:
                logger.warning(f"Could not save welcome message: {e}")
        
        return StartJourneyResponse(
            success=True,
            journey_id=journey_id,
            message="Companion journey started successfully",
            welcome_message=welcome_message
        )
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error starting companion journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def companion_chat(
    data: ChatRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """
    Chat with AI Wellness Companion with full context awareness, safety middleware, and intent decay monitoring.
    """
    try:
        # 1. Retrieve current journey state to verify if chat is already locked
        journey = None
        if data.journey_id:
            try:
                journey = await companion_manager.get_journey(data.journey_id)
            except HTTPException:

                raise

            except Exception as e:
                logger.warning(f"Error retrieving journey {data.journey_id}: {e}")

        # If the journey is already locked/referred or temporarily locked due to abuse, block further AI chat
        if journey:
            status = journey.get("status")
            metadata = journey.get("metadata") or {}
            
            # Check upfront abuse lock
            from datetime import datetime
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
                                detected_language="en",
                                intervention_type="escalation",
                                metadata={"abuse_locked": True, "lock_remaining": time_str}
                            )
                    except Exception as parse_ex:
                        logger.error(f"Error checking upfront abuse lock: {parse_ex}")

            if status == CompanionStatus.REFERRED.value or metadata.get("locked") is True:
                logger.warning(f"🛑 Chat request rejected: Journey {data.journey_id} is LOCKED due to prior safety escalation.")
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
                    detected_language="en",
                    intervention_type="escalation",
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
            logger.warning(f"⚠️ Critical medical safety concern detected: {safety_check['reason']}. Locking chat.")
            
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
                    
                    # Update status in DB and cache to Referred
                    await companion_manager.update_journey_status(
                        journey_id=data.journey_id,
                        status=CompanionStatus.REFERRED,
                        resolution_notes=f"Emergency safety lock: {safety_check['reason']}"
                    )
                    
                    # Persist metadata changes to DB if available
                    if companion_manager.client:
                        try:
                            companion_manager.client.table("companion_journeys").update({
                                "metadata": current_metadata,
                                "status": CompanionStatus.REFERRED.value
                            }).eq("id", data.journey_id).execute()
                        except Exception as db_ex:
                            logger.warning(f"Failed to persist journey metadata to DB: {db_ex}")
                    
                    # Persist in cache too
                    from app.companion_cache import companion_cache
                    cached_journey = companion_cache.get_journey(data.journey_id)
                    if cached_journey:
                        cached_journey["status"] = CompanionStatus.REFERRED.value
                        cached_journey["metadata"] = current_metadata
                        companion_cache.set_journey(data.journey_id, cached_journey)
                        
                except Exception as ex:
                    logger.error(f"Error locking journey during safety check: {ex}")

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
                detected_language="en",
                intervention_type="escalation",
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
        intent_status = await monitor_intent_decay(data.journey_id, data.message, data.language or "en")
        if intent_status["is_locked"]:
            logger.warning(f"🛑 Chat request locked due to Intent Decay: Journey {data.journey_id}")
            return ChatResponse(
                success=True,
                response=intent_status["lock_message"],
                language=data.language or "en",
                detected_language="en",
                intervention_type="escalation",
                metadata=intent_status["metadata"]
            )

        # 3. If safe, execute standard companion pipeline
        from app.astra.routes import pipeline_instance
        if not pipeline_instance:
            raise HTTPException(status_code=503, detail="Astra Pipeline not initialized")

        # Inject steering prompt if off-topic
        message_to_send = data.message
        if intent_status["steer_instruction"]:
            message_to_send += intent_status["steer_instruction"]

        # Process through the unified pipeline
        result = await pipeline_instance.run(
            input_text=message_to_send,
            user_uuid=data.journey_id, # Using journey_id as temporary UUID
            channel="app",
            metadata={
                "journey_id": data.journey_id,
                "feature": "companion",
                "journey_metadata": (journey.get("metadata") or {}) if journey else {}
            }
        )

        # Handle string or dict result from pipeline
        response_text = result if isinstance(result, str) else result.get("response", "")
        detected_lang = result.get("language", "en") if isinstance(result, dict) else "en"
        capability = result.get("capability", "CHECK_IN") if isinstance(result, dict) else "CHECK_IN"
        meta = result.get("metadata", {}) if isinstance(result, dict) else {}

        # Merge intent decay metadata
        meta.update(intent_status["metadata"])

        # --- XSS SANITIZATION (AI Output Scrubbing) ---
        response_text = xss_sanitizer.sanitize_text(response_text)

        tokens = len(response_text.split())
        pruned_flag = False
        if isinstance(result, dict):
            tokens = result.get("metadata", {}).get("tokens_used", tokens)
            pruned_flag = result.get("metadata", {}).get("pruned", False)

        # --- TOKEN BUDGET MONITOR ACCUMULATION ---
        user_id = journey.get("patient_id") if journey else None
        if journey and user_id:
            current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
            budget_key = f"token_usage:{user_id}:{current_hour}"
            
            estimated_tokens = int((len(data.message.split()) + len(response_text.split())) * 1.3)
            actual_tokens = tokens if tokens > 0 else estimated_tokens
            
            current_usage = redis_cache.get("budget", budget_key) or 0
            new_usage = current_usage + actual_tokens
            redis_cache.set("budget", budget_key, new_usage, ttl_seconds=7200)
            
            if new_usage > 2000:
                logger.critical(f"🚨 DENIAL OF WALLET PREVENTED: User {user_id} exceeded 2000 tokens/hr (Usage: {new_usage}). Freezing account.")
                redis_cache.set("budget", f"frozen:{user_id}", True, ttl_seconds=86400 * 365)
                
                try:
                    if db_manager.is_connected():
                        db_manager.client.table("patient_profiles").update({"is_active": False}).eq("patient_id", user_id).execute()
                except Exception as ex:
                    logger.error(f"Failed to update database for frozen user: {ex}")
                
                return ChatResponse(
                    success=True,
                    response=(
                        "⚠️ **ACCOUNT FROZEN FOR REVIEW** ⚠️\n\n"
                        "We detected unusually high activity on your account. To protect the platform and prevent abuse, "
                        "your AI Companion connection has been severed immediately.\n\n"
                        "Your account has been flagged for human review. Please contact support."
                    ),
                    language=data.language or "en",
                    detected_language="en",
                    intervention_type="escalation",
                    metadata={"account_frozen": True}
                )

        # IMMUTABLE AUDIT TRAIL LOGGING (Issue #12)
        audit_logger.log_event(
            event_type="ai_response",
            actor_id=user_id or "anonymous",
            action_details="AI Companion generated a medical/wellness response (Legacy API).",
            payload={
                "user_message": data.message,
                "ai_response": response_text,
                "pruned": pruned_flag,
                "tokens_used": actual_tokens if journey and user_id else tokens
            },
            session_id=data.journey_id
        )

        # Log interaction in journey
        try:
            await companion_manager.log_interaction(
                journey_id=data.journey_id,
                interaction_type=capability,
                content=response_text,
                language=detected_lang,
                metadata={"user_message": data.message}
            )
        except Exception as log_ex:
            logger.warning(f"Failed to log interaction: {log_ex}")

        return ChatResponse(
            success=True,
            response=response_text,
            language=data.language or "en",
            detected_language=detected_lang,
            intervention_type=capability,
            metadata=meta
        )
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error in companion chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journey/{journey_id}")
async def get_journey(
    journey_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get companion journey details"""
    try:
        journey = await companion_manager.get_journey(journey_id)
        if not journey:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        return {"success": True, "journey": journey}
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journey/user/{user_id}")
async def get_user_journeys(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20
):
    """Get all journeys for a user"""
    try:
        companion_status = CompanionStatus(status) if status else None
        journeys = await companion_manager.get_user_journeys(
            user_id=user_id,
            status=companion_status,
            limit=limit
        )
        
        return {
            "success": True,
            "journeys": journeys,
            "total": len(journeys)
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting user journeys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/journey/{journey_id}/status")
async def update_journey_status(
    journey_id: str,
    status: str,
    resolution_notes: Optional[str] = None
):
    """Update journey status (active, monitoring, resolved, etc.)"""
    try:
        companion_status = CompanionStatus(status)
        success = await companion_manager.update_journey_status(
            journey_id=journey_id,
            status=companion_status,
            resolution_notes=resolution_notes
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update journey status")
        
        return {
            "success": True,
            "message": f"Journey status updated to {status}"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error updating journey status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CASE MANAGEMENT ENDPOINTS ============

@router.post("/case/create", response_model=CreateCaseResponse)
async def create_health_case(request: CreateCaseRequest):
    """
    Create a health case after doctor consultation
    """
    try:
        case_id = await companion_manager.create_case(
            journey_id=request.journey_id,
            user_id=request.user_id,
            doctor_id=request.doctor_id,
            diagnosis=request.diagnosis,
            prescription_id=request.prescription_id,
            diet_plan=request.diet_plan,
            treatment_duration_days=request.treatment_duration_days,
            follow_up_schedule=request.follow_up_schedule,
            metadata=request.metadata
        )
        
        if not case_id:
            raise HTTPException(status_code=500, detail="Failed to create case")
        
        return CreateCaseResponse(
            success=True,
            case_id=case_id,
            message=f"Case created successfully. Companion will support patient for {request.treatment_duration_days} days."
        )
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error creating case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case/{case_id}")
async def get_case(case_id: str):
    """Get case details"""
    try:
        case = await companion_manager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {"success": True, "case": case}
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/case/progress")
async def update_case_progress(request: UpdateProgressRequest):
    """
    Update case progress and adherence
    """
    try:
        success = await companion_manager.update_case_progress(
            case_id=request.case_id,
            progress_percentage=request.progress_percentage,
            adherence_score=request.adherence_score,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update case progress")
        
        # Auto-resolve journey if case is 100% complete
        if request.progress_percentage >= 100:
            case = await companion_manager.get_case(request.case_id)
            if case:
                await companion_manager.update_journey_status(
                    journey_id=case["journey_id"],
                    status=CompanionStatus.RESOLVED,
                    resolution_notes="Treatment completed successfully"
                )
        
        return {
            "success": True,
            "message": f"Progress updated to {request.progress_percentage}%"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error updating case progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ MILESTONE & HEALTH RECORDS ENDPOINTS ============

@router.post("/milestone/add")
async def add_milestone(request: MilestoneRequest):
    """Add a milestone achievement to the journey"""
    try:
        success = await companion_manager.add_milestone(
            journey_id=request.journey_id,
            milestone_type=request.milestone_type,
            description=request.description,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add milestone")
        
        return {
            "success": True,
            "message": "Milestone added successfully"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error adding milestone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journey/{journey_id}/records")
async def get_journey_health_records(journey_id: str):
    """Get all health records linked to a journey"""
    try:
        records = await companion_manager.get_journey_records(journey_id)
        
        return {
            "success": True,
            "records": records,
            "total": len(records)
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting journey records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/journey/{journey_id}/link-record")
async def link_health_record(
    journey_id: str,
    record_type: str = Body(...),
    storj_document_id: str = Body(...),
    description: str = Body(...)
):
    """Link a Storj health record to the journey"""
    try:
        success = await companion_manager.link_health_record(
            journey_id=journey_id,
            record_type=record_type,
            storj_document_id=storj_document_id,
            description=description
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to link health record")
        
        return {
            "success": True,
            "message": "Health record linked successfully"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error linking health record: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CONVERSATION HISTORY ENDPOINTS ============

@router.get("/conversation/{user_id}")
async def get_conversation_history(
    user_id: str,
    session_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get conversation history from Supabase
    """
    try:
        if session_id:
            # Get specific session history
            history = await db_manager.get_chat_history(session_id, limit=limit)
        else:
            # Get all user sessions
            sessions = await db_manager.get_user_sessions(user_id, limit=1)
            if sessions:
                history = await db_manager.get_chat_history(sessions[0]["id"], limit=limit)
            else:
                history = []
        
        return {
            "success": True,
            "conversation": history,
            "total_messages": len(history)
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
