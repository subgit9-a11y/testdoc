"""
Enhanced Astra API Routes - Voice, Knowledge, Nudges, Telemedicine

New endpoints for advanced Astra features:
- Voice input/output
- Ayurvedic knowledge base
- Proactive nudges
- Telemedicine integration
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from .voice_service import VoiceService
from .ayurvedic_knowledge import AyurvedicKnowledgeBase
from .nudge_engine import ProactiveNudgeEngine, NudgeType
from .telemedicine_bridge import TelemedicineBridge, DoctorSpecialization

logger = logging.getLogger(__name__)

# Initialize services
voice_service = VoiceService()
ayurvedic_kb = AyurvedicKnowledgeBase()
nudge_engine = ProactiveNudgeEngine()
telemedicine = TelemedicineBridge()

# Create router
enhanced_router = APIRouter(prefix="/astra/enhanced", tags=["Astra Enhanced"])


# ==================== VOICE ENDPOINTS ====================

class VoiceInputRequest(BaseModel):
    language_code: Optional[str] = "en-IN"
    audio_format: str = "wav"


@enhanced_router.post("/voice/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    language_code: Optional[str] = "en-IN"
):
    """
    Convert speech to text.
    
    Upload audio file and get transcription.
    """
    try:
        audio_data = await audio.read()
        
        result = await voice_service.speech_to_text(
            audio_data=audio_data,
            language_code=language_code
        )
        
        return result
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TTSRequest(BaseModel):
    text: str
    language_code: Optional[str] = "en-IN"
    voice_name: Optional[str] = None
    speaking_rate: float = 1.0


@enhanced_router.post("/voice/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech.
    
    Returns audio file.
    """
    try:
        result = await voice_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            speaking_rate=request.speaking_rate
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return StreamingResponse(
            iter([result["audio_data"]]),
            media_type=f"audio/{result['format']}"
        )
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_router.get("/voice/supported-languages")
async def get_supported_languages():
    """Get list of supported languages for voice"""
    return voice_service.get_supported_languages()


# ==================== AYURVEDIC KNOWLEDGE ENDPOINTS ====================

@enhanced_router.get("/knowledge/herb/{herb_name}")
async def get_herb_info(herb_name: str):
    """
    Get detailed information about an Ayurvedic herb.
    """
    herb = ayurvedic_kb.search_herb(herb_name)
    
    if not herb:
        raise HTTPException(status_code=404, detail=f"Herb '{herb_name}' not found")
    
    return {
        "name_en": herb.name_en,
        "name_hi": herb.name_hi,
        "name_sa": herb.name_sa,
        "botanical_name": herb.botanical_name,
        "properties": herb.properties,
        "doshas_balanced": herb.doshas_balanced,
        "uses": herb.uses,
        "contraindications": herb.contraindications,
        "common_forms": herb.common_forms
    }


@enhanced_router.get("/knowledge/dosha/{dosha_name}")
async def get_dosha_info(dosha_name: str):
    """
    Get detailed information about a dosha.
    """
    dosha = ayurvedic_kb.get_dosha_info(dosha_name)
    
    if not dosha:
        raise HTTPException(status_code=404, detail=f"Dosha '{dosha_name}' not found")
    
    return {
        "name": dosha.name,
        "elements": dosha.elements,
        "qualities": dosha.qualities,
        "physical_traits": dosha.physical_traits,
        "mental_traits": dosha.mental_traits,
        "imbalance_symptoms": dosha.imbalance_symptoms,
        "balancing_foods": dosha.balancing_foods,
        "balancing_lifestyle": dosha.balancing_lifestyle
    }


@enhanced_router.get("/knowledge/remedy/{ailment}")
async def get_remedy(ailment: str):
    """
    Get Ayurvedic remedy for common ailment.
    """
    remedy = ayurvedic_kb.get_remedy_for_ailment(ailment)
    
    if not remedy:
        raise HTTPException(status_code=404, detail=f"Remedy for '{ailment}' not found")
    
    return {
        "ailment": remedy.ailment,
        "dosha_imbalance": remedy.dosha_imbalance,
        "herbs": remedy.herbs,
        "dietary_advice": remedy.dietary_advice,
        "lifestyle_advice": remedy.lifestyle_advice,
        "precautions": remedy.precautions
    }


@enhanced_router.get("/knowledge/herbs")
async def list_all_herbs():
    """List all available herbs in knowledge base"""
    return {
        "total_count": len(ayurvedic_kb.herbs),
        "herbs": ayurvedic_kb.get_all_herbs()
    }


@enhanced_router.get("/knowledge/dietary-guidelines/{dosha}")
async def get_dietary_guidelines(dosha: str):
    """Get dietary guidelines for specific dosha"""
    guidelines = ayurvedic_kb.get_dietary_guidelines(dosha)
    
    if not guidelines:
        raise HTTPException(status_code=404, detail=f"Guidelines for '{dosha}' not found")
    
    return guidelines


# ==================== NUDGE ENGINE ENDPOINTS ====================

@enhanced_router.post("/nudges/generate/{user_id}/{profile_id}")
async def generate_nudges(user_id: str, profile_id: str):
    """
    Generate personalized nudges for user.
    """
    try:
        nudges = await nudge_engine.generate_nudges(user_id, profile_id)
        
        return {
            "success": True,
            "count": len(nudges),
            "nudges": [
                {
                    "nudge_id": n.nudge_id,
                    "type": n.nudge_type.value,
                    "priority": n.priority.value,
                    "title": n.title,
                    "message": n.message,
                    "action_url": n.action_url,
                    "scheduled_time": n.scheduled_time.isoformat(),
                    "delivery_channels": n.delivery_channels
                }
                for n in nudges
            ]
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Nudge generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_router.get("/nudges/engagement/{user_id}/{profile_id}")
async def get_engagement_profile(user_id: str, profile_id: str):
    """
    Get user engagement analytics.
    """
    try:
        profile = await nudge_engine.analyze_user_behavior(user_id, profile_id)
        
        return {
            "user_id": profile.user_id,
            "profile_id": profile.profile_id,
            "last_active": profile.last_active.isoformat(),
            "total_sessions": profile.total_sessions,
            "avg_session_duration": profile.avg_session_duration,
            "medicine_adherence_rate": profile.medicine_adherence_rate,
            "symptom_log_frequency": profile.symptom_log_frequency,
            "preferred_nudge_time": profile.preferred_nudge_time,
            "engagement_score": profile.engagement_score,
            "streak_days": profile.streak_days
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Engagement analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TELEMEDICINE ENDPOINTS ====================

class EscalationCheckRequest(BaseModel):
    user_query: str
    intent_class: str
    conversation_history: List[dict]
    symptoms: Optional[List[str]] = []


@enhanced_router.post("/telemedicine/check-escalation")
async def check_escalation(request: EscalationCheckRequest):
    """
    Check if query should be escalated to doctor.
    """
    try:
        result = await telemedicine.should_escalate(
            user_query=request.user_query,
            intent_class=request.intent_class,
            conversation_history=request.conversation_history,
            symptoms=request.symptoms
        )
        
        return result
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Escalation check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DoctorSearchRequest(BaseModel):
    specialization: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    max_results: int = 5


@enhanced_router.post("/telemedicine/find-doctors")
async def find_doctors(request: DoctorSearchRequest):
    """
    Find matching doctors based on criteria.
    """
    try:
        # Convert specialization string to enum
        spec_enum = None
        if request.specialization:
            try:
                spec_enum = DoctorSpecialization[request.specialization.upper()]
            except KeyError:
                pass
        
        doctors = await telemedicine.find_matching_doctors(
            specialization=spec_enum,
            language=request.language,
            location=request.location,
            max_results=request.max_results
        )
        
        return {
            "success": True,
            "count": len(doctors),
            "doctors": [
                {
                    "doctor_id": d.doctor_id,
                    "name": d.name,
                    "specialization": d.specialization.value,
                    "qualifications": d.qualifications,
                    "experience_years": d.experience_years,
                    "languages": d.languages,
                    "rating": d.rating,
                    "consultation_fee": d.consultation_fee,
                    "available_slots": [slot.isoformat() for slot in d.available_slots],
                    "is_verified": d.is_verified,
                    "location": d.location
                }
                for d in doctors
            ]
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Doctor search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class PreConsultationRequest(BaseModel):
    user_id: str
    profile_id: str
    conversation_history: List[dict]
    symptoms: List[str]


@enhanced_router.post("/telemedicine/pre-consultation-summary")
async def generate_pre_consultation_summary(request: PreConsultationRequest):
    """
    Generate AI-powered pre-consultation summary for doctor.
    """
    try:
        summary = await telemedicine.generate_pre_consultation_summary(
            user_id=request.user_id,
            profile_id=request.profile_id,
            conversation_history=request.conversation_history,
            symptoms=request.symptoms
        )
        
        return {
            "summary_id": summary.summary_id,
            "patient_name": summary.patient_name,
            "age": summary.age,
            "gender": summary.gender,
            "chief_complaint": summary.chief_complaint,
            "symptoms": summary.symptoms,
            "symptom_duration": summary.symptom_duration,
            "previous_consultations": summary.previous_consultations,
            "current_medications": summary.current_medications,
            "allergies": summary.allergies,
            "dosha_assessment": summary.dosha_assessment,
            "ai_conversation_summary": summary.ai_conversation_summary,
            "red_flags": summary.red_flags,
            "suggested_focus_areas": summary.suggested_focus_areas
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Pre-consultation summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AppointmentBookingRequest(BaseModel):
    user_id: str
    profile_id: str
    doctor_id: str
    slot_time: str  # ISO format
    consultation_type: str = "video"


@enhanced_router.post("/telemedicine/book-appointment")
async def book_appointment(request: AppointmentBookingRequest):
    """
    Book appointment with doctor.
    """
    try:
        slot_time = datetime.fromisoformat(request.slot_time)
        
        result = await telemedicine.book_appointment(
            user_id=request.user_id,
            profile_id=request.profile_id,
            doctor_id=request.doctor_id,
            slot_time=slot_time,
            consultation_type=request.consultation_type
        )
        
        return result
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Appointment booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH CHECK ====================

@enhanced_router.get("/health")
async def enhanced_features_health():
    """Health check for enhanced features"""
    return {
        "status": "healthy",
        "features": {
            "voice": {
                "stt_available": voice_service.speech_client is not None or voice_service.whisper_model is not None,
                "tts_available": voice_service.tts_client is not None
            },
            "knowledge_base": {
                "herbs_count": len(ayurvedic_kb.herbs),
                "doshas_count": len(ayurvedic_kb.doshas),
                "remedies_count": len(ayurvedic_kb.remedies)
            },
            "nudge_engine": {
                "status": "operational"
            },
            "telemedicine": {
                "status": "operational"
            }
        }
    }
