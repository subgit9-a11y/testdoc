"""
Order Management API (Supabase Powered)
Handles prescription storage, order tracking, and status updates via Supabase.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
import logging
from datetime import datetime, timezone
import uuid

from app.database import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Order Management"])

class PrescriptionCreateRequest(BaseModel):
    patient_id: str
    doctor_id: str
    consultation_id: Optional[str] = None
    diagnosis: str
    notes: Optional[str] = None
    medicines: List[Dict[str, Any]]

class StatusUpdateRequest(BaseModel):
    prescription_id: str
    new_status: str
    change_reason: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = {}

@router.post("/prescription/save")
async def save_prescription_record(prescription_data: PrescriptionCreateRequest):
    """Save prescription record to Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        prescription_id = f"PRES-{uuid.uuid4().hex[:8].upper()}"
        
        # Prepare main record
        record = {
            "prescription_id": prescription_id,
            "patient_id": prescription_data.patient_id,
            "doctor_id": prescription_data.doctor_id,
            "diagnosis": prescription_data.diagnosis,
            "notes": prescription_data.notes or "",
            "status": "created",
            "prescribed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Prepare medicines
        medicines = []
        for med in prescription_data.medicines:
            medicines.append({
                "medicine_name": med.get("medicine_name"),
                "quantity": med.get("quantity", 1),
                "dose": med.get("dose", ""),
                "schedule": med.get("schedule", ""),
                "timing": med.get("timing", ""),
                "duration": med.get("duration", "7 days"),
                "instructions": med.get("instructions", "")
            })
        
        await db_manager.create_prescription(record, medicines)
        
        return {
            "success": True,
            "prescription_id": prescription_id,
            "status": "created",
            "message": "Prescription saved to Supabase"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Failed to save prescription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}")
async def get_patient_order_history(patient_id: str):
    """Get history from Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Complex query with prescribed_medicines
        res = db_manager.client.table("prescription_records").select("*, prescribed_medicines(*)").eq("patient_id", patient_id).order("prescribed_at", desc=True).execute()
        
        return {
            "patient_id": patient_id,
            "total_prescriptions": len(res.data) if res.data else 0,
            "prescriptions": res.data or []
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prescription/{prescription_id}")
async def get_prescription_details(prescription_id: str):
    """Get details from Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    prescription = await db_manager.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    return prescription