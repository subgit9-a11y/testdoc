import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any

from app.shopify_models import PrescriptionRequest
from app.automated_prescription_service import automated_prescription_service
from app.firebase_auth_middleware import require_doctor_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prescriptions", tags=["Prescription Submission"])

@router.post("/submit-and-automate")
async def submit_prescription_automated(
    request: PrescriptionRequest,
    doctor_id: str = Query(..., description="Unique ID of the doctor"),
    patient_id: str = Query(..., description="Unique ID of the patient"),
    doctor: Dict[str, Any] = Depends(require_doctor_auth)
):
    """
    Doctors use this endpoint to submit a final prescription.
    
    This triggers:
    1. Saving to database (Record + Medicines) via Supabase
    2. Creating a Shopify Draft Order (Auto-Cart)
    3. Generating a PDF and uploading to Wasabi
    4. Sending a WhatsApp notification with the PDF link and Invoice URL
    5. Scheduling medicine reminders for the patient
    """
    try:
        logger.info(f"Received automated prescription submission for patient {patient_id} from doctor {doctor_id}")
        
        result = await automated_prescription_service.process_prescription(
            prescription_data=request,
            doctor_id=doctor_id,
            patient_id=patient_id
        )
        
        if not result["success"]:
            # If there's a critical error, return 500
            if any("Critical Error" in e for e in result["errors"]):
                raise HTTPException(status_code=500, detail=result["errors"])
        
        return result
        
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error in prescription submission route: {e}")
        raise HTTPException(status_code=500, detail=str(e))
