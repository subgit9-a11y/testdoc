import logging
import json
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.auth_middleware import verify_api_key
from app.security.disha_compliance import DISHACompliance, DataAccessPurpose

# Core inference engine - REFACTORED to use unified Astra Companion client
try:
    from app.astra_brain_client import get_brain_client as get_engine
    from app.config import settings
except ImportError:
    # Fallback for systems without updated client
    def get_engine():
        from app.enhanced_inference import AstraModelInference
        return AstraModelInference()
    settings = type('Settings', (object,), {'BASE_MODEL': 'llama', 'LORA_MODEL': 'lora'})()

logger = logging.getLogger(__name__)

# Spec says paths like /v1/chat, so we use /v1 as prefix
router = APIRouter(prefix="/v1", tags=["Astra Brain AI"])

# Singleton retrieval is handled by get_brain_client

# ============================================================================
# Request Models
# ============================================================================

class ChatRequest(BaseModel):
    q: str

class AutopilotRequest(BaseModel):
    q: str

class FillRequest(BaseModel):
    text: str
    schema_def: str

class ProfileAnalysisRequest(BaseModel):
    p_a: str
    task: str = "buddy_match"
    p_b: Optional[str] = None

class WellnessRequest(BaseModel):
    topic: str
    duration: str = "5 mins"

class ToneRequest(BaseModel):
    text: str
    target_tone: str = "polite"

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/")
async def brain_root():
    return {"status": "ok", "service": "Astra AI Engine"}

@router.get("/health")
async def brain_health():
    e = get_engine()
    return {"status": "online" if e.is_loaded() else "loading", "connected": True}

@router.post("/chat")
async def brain_chat(request: ChatRequest):
    e = get_engine()
    try:
        res = await e.chat(request.q)
        if res.success:
            return {"success": True, "answer": res.answer, "mode": res.mode}
        return {"success": False, "answer": res.answer, "mode": "error"}
    except Exception as ex:
        return {"success": False, "answer": str(ex), "mode": "error"}

@router.post("/autopilot")
async def brain_autopilot(request: AutopilotRequest):
    e = get_engine()
    try:
        res = await e.autopilot(request.q)
        return {"intent": res.intent.value, "status": res.status, "should_route": res.intent.value != "CHAT"}
    except Exception:
        return {"intent": "CHAT", "status": "error", "should_route": False}

@router.post("/fill")
async def brain_fill(request: FillRequest):
    e = get_engine()
    try:
        res = await e.fill(request.text, request.schema_def)
        return res
    except Exception as ex:
        return {"success": False, "error": str(ex)}

@router.post("/shop_assist")
async def brain_shop_assist(q: str = Body(..., title="Q", embed=False)):
    e = get_engine()
    try:
        res = await e.shop_assist(q)
        return res
    except Exception as ex:
        return {"success": False, "error": str(ex)}

@router.post("/extract_schedule", dependencies=[Depends(verify_api_key)])
async def brain_extract_schedule(request: Request, text: str = Body(..., title="Text", embed=False)):
    e = get_engine()
    res = await e.extract_schedule(text)
    return {"success": True, "schedule_json": res.raw_json, "reminders": res.reminders}

@router.post("/doctor_summary", dependencies=[Depends(verify_api_key)])
async def brain_doctor_summary(notes: str = Body(..., title="Notes", embed=False)):
    e = get_engine()
    res = await e.doctor_summary(notes)
    return res

@router.post("/analyze_safety", dependencies=[Depends(verify_api_key)])
async def brain_analyze_safety(text: str = Body(..., title="Text", embed=False)):
    e = get_engine()
    res = await e.analyze_safety(text)
    return {
        "is_safe": res.is_safe,
        "risk_level": res.risk_level,
        "flags": res.flags
    }

@router.post("/detect_emotion")
async def brain_detect_emotion(q: str = Body(..., title="Q", embed=False)):
    e = get_engine()
    res = await e.detect_emotion(q)
    return {"success": True, "emotion": res.emotion, "intensity": res.intensity}

@router.post("/profile_analysis")
async def brain_profile_analysis(request: ProfileAnalysisRequest):
    e = get_engine()
    res = await e.profile_analysis(request.p_a, request.task, request.p_b)
    return res

@router.post("/generate_wellness")
async def brain_generate_wellness(request: WellnessRequest):
    e = get_engine()
    res = await e.generate_wellness(request.topic, request.duration)
    return res

@router.post("/adjust_tone")
async def brain_adjust_tone(request: ToneRequest):
    e = get_engine()
    res = await e.adjust_tone(request.text, request.target_tone)
    return res

@router.get("/endpoints")
async def list_brain_endpoints():
    return {"base_url": "https://metal-rotary-nano-heavily.trycloudflare.com", "version": "1.0-automated"}

