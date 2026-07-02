from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import json
import logging

from app.astra_brain_client import get_brain_client
from app.firebase_auth_middleware import require_firebase_auth

logger = logging.getLogger(__name__)

# Router for the Brain Gateway (Astra Companion)
brain_router = APIRouter(prefix="/api/v1/brain", tags=["brain"])

# --- Request Models ---

class ChatRequest(BaseModel):
    q: Optional[str] = Field(None, description="The user's query (legacy field)")
    message: Optional[str] = Field(None, description="The user's query (Flutter Doctor App field)")
    user_id: Optional[str] = Field(None, description="User ID for context")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Extra user metadata")

class ExtractScheduleRequest(BaseModel):
    prescription_text: str = Field(..., description="Medical text to parse")

class SummaryRequest(BaseModel):
    notes: str

class SafetyRequest(BaseModel):
    text: str

class ToneRequest(BaseModel):
    text: str
    target_tone: str = "polite"

# --- Endpoints ---

@brain_router.get("/health")
async def brain_health_check() -> Dict[str, Any]:
    """Health check that verifies connection to the AI engine via Cloudflare Tunnel"""
    brain = get_brain_client()
    status = await brain.check_health()
    return {"status": "online", "engine_api": status}

@brain_router.post("/chat")
async def brain_chat(request: ChatRequest):
    """Real AI Chat Streaming Endpoint"""
    query = request.q or request.message or ""
    if not query:
        raise HTTPException(status_code=400, detail="Provide either 'q' or 'message' field")
        
    # INJECT GPS COORDINATES FOR MCP WEATHER TOOL
    if request.user_metadata:
        lat = request.user_metadata.get("latitude")
        lon = request.user_metadata.get("longitude")
        if lat and lon:
            query = f"{query}\n\n[System Context: User Location is Latitude {lat}, Longitude {lon}. Use this for weather API.]"
    
    brain = get_brain_client()
    
    async def event_stream():
        async for chunk in brain.chat_stream(query):
            yield chunk
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@brain_router.post("/shop_assist")
async def brain_shop_assist(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    """AI Product mapping for Shopify inventory"""
    brain = get_brain_client()
    result = await brain.shop_assist(query)
    return result

@brain_router.post("/extract_schedule")
async def brain_extract_schedule(request: ExtractScheduleRequest) -> Dict[str, Any]:
    """Parses medical text into structured dosage JSON"""
    brain = get_brain_client()
    result = await brain.extract_schedule(request.prescription_text)
    return {
        "success": True,
        "schedule_json": result.raw_json,
        "reminders": result.reminders
    }

@brain_router.post("/doctor_summary")
async def brain_doctor_summary(request: SummaryRequest) -> Dict[str, Any]:
    """Generates clinical summaries for doctors"""
    brain = get_brain_client()
    result = await brain.doctor_summary(request.notes)
    return result

@brain_router.post("/analyze_safety")
async def brain_analyze_safety(request: SafetyRequest) -> Dict[str, Any]:
    """Performs medical risk analysis"""
    brain = get_brain_client()
    result = await brain.analyze_safety(request.text)
    return {
        "is_safe": result.is_safe,
        "risk_level": result.risk_level,
        "flags": result.flags
    }

@brain_router.post("/adjust_tone")
async def brain_adjust_tone(request: ToneRequest) -> Dict[str, Any]:
    """Adjusts clinical notes tone"""
    brain = get_brain_client()
    result = await brain.adjust_tone(request.text, request.target_tone)
    return result
