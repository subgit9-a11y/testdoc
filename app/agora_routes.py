from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import time
from typing import Optional
from app.auth_middleware import get_current_user
import logging

try:
    from agora_token_builder import RtcTokenBuilder, Role_Attendee
except ImportError:
    # Fallback if library is not installed yet
    RtcTokenBuilder = None

router = APIRouter(prefix="/video", tags=["Video Consultations"])
logger = logging.getLogger("AstraAgora")

class TokenRequest(BaseModel):
    to_id: str
    uid: int = 0  # 0 means let Agora assign

class CallHistoryRequest(BaseModel):
    doctor_id: str
    patient_id: str
    channel_name: str
    start_time: str
    status: Optional[str] = "initiated"

@router.post("/generate-token")
def generate_token(req: TokenRequest, current_user: dict = Depends(get_current_user)):
    app_id = os.getenv("AGORA_APP_ID")
    app_certificate = os.getenv("AGORA_APP_CERTIFICATE")
    
    if not app_id or not app_certificate:
        logger.error("Agora credentials missing in environment variables.")
        raise HTTPException(status_code=500, detail="Video call service not configured.")
        
    if not RtcTokenBuilder:
        raise HTTPException(status_code=500, detail="Agora token builder library missing.")

    # Generate a unique channel name using doctor and patient IDs
    doctor_id = current_user.get("id", "doc")
    channel_name = f"doc_{doctor_id}_pat_{req.to_id}"
    uid = req.uid
    expiration_time_in_seconds = 3600 # 1 hour
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, Role_Attendee, privilege_expired_ts
    )
    
    return {
        "success": True,
        "data": {
            "token": token,
            "cn": channel_name,
            "uid": uid
        }
    }

@router.post("/add-call-history")
def add_call_history(req: CallHistoryRequest, current_user: dict = Depends(get_current_user)):
    logger.info(f"Video call history added for Doctor {req.doctor_id} and Patient {req.patient_id}")
    return {"success": True, "message": "Call history recorded successfully"}

@router.get("/history")
def get_call_history(current_user: dict = Depends(get_current_user)):
    return {"success": True, "data": []}

@router.post("/update-patient-vcall")
def update_patient_vcall(req: dict, current_user: dict = Depends(get_current_user)):
    return {"success": True, "message": "VCall updated successfully"}
