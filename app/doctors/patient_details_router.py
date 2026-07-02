"""
Aggregated Patient Details Router for Doctors (Supabase Powered)
Provides a comprehensive view of patient history, AI intake, and profile details via Supabase.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.database import db_manager
from app.astra_fill.service import astra_fill_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/doctors/patient-view", tags=["Doctor View"])

# Pydantic Models for Response
class PatientComprehensiveView(BaseModel):
    patient_profile: Dict[str, Any]
    latest_astra_fill: Optional[Dict[str, Any]] = None
    recent_consultations: List[Dict[str, Any]] = []
    prescription_history: List[Dict[str, Any]] = []

@router.get("/{patient_id}", response_model=PatientComprehensiveView)
async def get_patient_comprehensive_view(
    patient_id: str
):
    """
    Fetch all relevant patient details from Supabase for the doctor to review.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
        
    try:
        # 1. Get Patient Profile from Supabase
        patient = await db_manager.get_patient_profile(patient_id)
        if not patient:
            # Fallback search by patient_code
            res = db_manager.client.table("patient_profiles").select("*").eq("patient_code", patient_id).execute() if db_manager.client else None
            if res and res.data:
                patient = res.data[0]
            else:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        # Canonical patient_id
        patient_id = patient.get("patient_id")

        # 2. Get Latest Astra Fill (AI Intake) from Supabase
        latest_fill = None
        if db_manager.client:
            res_fill = db_manager.client.table("astra_fill_extractions").select("*").eq("status", "pending").order("created_at", desc=True).limit(1).execute()
            if res_fill.data:
                latest_fill = res_fill.data[0]

        # 3. Get Recent Consultations from Supabase
        consultations = await db_manager.get_patient_consultations(patient_id, limit=5)

        # 4. Get Prescription History from Supabase
        prescriptions = await db_manager.get_patient_prescriptions(patient_id, limit=5)

        # Build response
        return PatientComprehensiveView(
            patient_profile=patient,
            latest_astra_fill=latest_fill,
            recent_consultations=[{
                "consultation_id": c.get("consultation_id"),
                "doctor_name": c.get("doctor_name"),
                "diagnosis": c.get("diagnosis"),
                "notes": c.get("notes"),
                "date": c.get("appointment_date") or c.get("created_at")
            } for c in consultations],
            prescription_history=[{
                "prescription_id": p.get("prescription_id"),
                "diagnosis": p.get("diagnosis"),
                "total_amount": p.get("total_amount"),
                "status": p.get("status"),
                "date": p.get("prescribed_at")
            } for p in prescriptions]
        )

    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error fetching comprehensive patient view: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching patient view")
