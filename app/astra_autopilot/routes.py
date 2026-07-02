"""
Astra Autopilot API Routes
Exposes endpoints for the frontend to manage Autopilot consent and view status.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from app.astra_autopilot.state_manager import AutopilotStateManager

router = APIRouter(prefix="/autopilot", tags=["Astra Autopilot"])

# Response Models
class AutopilotStatusResponse(BaseModel):
    patient_id: str
    is_enabled: bool
    care_journey_stage: str
    last_check: Optional[datetime]
    pending_action: Optional[Dict[str, Any]]

class ConsentRequest(BaseModel):
    patient_id: str
    consent_granted: bool

# Dependency
def get_state_manager():
    return AutopilotStateManager()

@router.get("/status/{patient_id}", response_model=AutopilotStatusResponse)
async def get_autopilot_status(
    patient_id: str,
    manager: AutopilotStateManager = Depends(get_state_manager)
):
    """
    Get the current Autopilot state for a patient.
    """
    state = manager.get_or_create_state(patient_id)
    if not state:
        raise HTTPException(status_code=500, detail="Could not fetch autopilot state")
    
    return AutopilotStatusResponse(
        patient_id=state.get("patient_id"),
        is_enabled=state.get("is_autopilot_enabled", False),
        care_journey_stage=state.get("care_journey_stage", "new"),
        last_check=state.get("last_autopilot_check"),
        pending_action=state.get("pending_autopilot_action")
    )

@router.post("/consent")
async def update_autopilot_consent(
    request: ConsentRequest,
    manager: AutopilotStateManager = Depends(get_state_manager)
):
    """
    Enable or Disable Astra Autopilot for a patient.
    """
    success = manager.update_state(request.patient_id, {
        "is_autopilot_enabled": request.consent_granted
    })
    
    if not success:
         raise HTTPException(status_code=500, detail="Failed to update consent")
         
    status_msg = "enabled" if request.consent_granted else "disabled"
    return {"message": f"Astra Autopilot {status_msg} successfully", "status": status_msg}

@router.get("/debug/trigger/{patient_id}")
async def debug_trigger_engine(patient_id: str):
    """
    DEV ONLY: Manually trigger the AI-governed autopilot for a specific patient.
    """
    try:
        from app.astra.routes import pipeline_instance
        if not pipeline_instance:
            raise HTTPException(status_code=503, detail="Astra Pipeline not initialized")
            
        # Autopilot as an AI-governed process
        result = await pipeline_instance.run(
            input_text="EVALUATE_PATIENT_CARE_JOURNEY",
            user_uuid=patient_id,
            channel="app",
            metadata={"feature": "autopilot", "is_automatic": True}
        )
        return result
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Autopilot trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

