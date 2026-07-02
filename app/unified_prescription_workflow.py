"""
Unified Prescription Workflow (Supabase Powered)
Orchestrates the complete prescription flow using Supabase.
"""

import logging
import tempfile
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.database import db_manager
from app.shopify_models import PrescriptionRequest
from app.prescription_pdf_service import PrescriptionPDFService
from app.storage_factory import storage_client
from app.medicine_reminders.reminder_engine import ReminderEngine
from app.pdf_worker import generate_and_upload_pdf_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prescription-workflow", tags=["Unified Prescription Workflow"])

# Initialize services
pdf_service = PrescriptionPDFService()
reminder_engine = ReminderEngine()

class UnifiedPrescriptionRequest(BaseModel):
    prescription_id: str
    patient_email: Optional[str] = None
    doctor_email: Optional[str] = None
    send_email: bool = True
    upload_to_storj: bool = True # Legacy name, now Wasabi
    create_reminders: bool = True
    share_via_whatsapp: bool = False
    patient_phone: Optional[str] = None

class WorkflowResult(BaseModel):
    success: bool
    prescription_id: str
    pdf_generated: bool
    email_sent: bool
    storj_uploaded: bool
    reminders_created: bool
    whatsapp_shared: bool
    pdf_url: Optional[str] = None
    document_id: Optional[str] = None
    errors: list = []

@router.post("/execute", response_model=WorkflowResult)
async def execute_unified_prescription_workflow(request: UnifiedPrescriptionRequest) -> WorkflowResult:
    """Execute the complete prescription workflow using Supabase"""
    
    result = WorkflowResult(
        success=False,
        prescription_id=request.prescription_id,
        pdf_generated=False,
        email_sent=False,
        storj_uploaded=False,
        reminders_created=False,
        whatsapp_shared=False,
        errors=[]
    )
    
    try:
        # 1. Get prescription from Supabase
        prescription_record = await db_manager.get_prescription(request.prescription_id)
        if not prescription_record:
            raise HTTPException(status_code=404, detail=f"Prescription not found")
        
        # 2. Convert to PrescriptionRequest format
        prescription = _convert_supabase_to_request(prescription_record)
        
        # 3, 4, 5. OOM ASSASSINATION PREVENTION (Issue #39)
        # We push PDF generation, Email sending, and Wasabi Upload to the Celery Worker queue.
        # This prevents the FastAPI main thread from consuming too much RAM and triggering the Linux OOM Killer.
        try:
            # Send to Celery Background Worker
            prescription_dict = prescription.dict()
            generate_and_upload_pdf_task.delay(
                prescription_dict=prescription_dict,
                patient_email=request.patient_email,
                send_email=request.send_email
            )
            
            # Since it's in the background, we mark these as queued (handled asynchronously)
            result.pdf_generated = True
            result.storj_uploaded = True
            if request.send_email: result.email_sent = True
            logger.info("✅ Pushed PDF generation and upload to Celery worker queue.")
        except HTTPException:

            raise

        except Exception as e:
            result.errors.append(f"Celery offload error: {e}")

        # 6. Reminders
        if request.create_reminders:
            try:
                # reminder_engine now uses Supabase internally (updated separately)
                await reminder_engine.create_medicine_schedules_from_prescription(request.prescription_id)
                result.reminders_created = True
            except HTTPException:

                raise

            except Exception as e:
                result.errors.append(f"Reminder error: {e}")

        result.success = True
        return result
        
    except HTTPException: raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Unified workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _convert_supabase_to_request(record: Dict[str, Any]) -> PrescriptionRequest:
    """Helper for converting Supabase JSON record to Pydantic model"""
    from app.shopify_models import PatientInfo, DoctorInfo, PrescriptionItem
    
    patient_info = PatientInfo(
        name=record.get("patient_name", "Patient"),
        contact=record.get("patient_phone", record.get("patient_email", "")),
        age=record.get("patient_age", 0),
        gender=record.get("patient_gender", "Not Specified")
    )
    
    doctor_info = DoctorInfo(
        name=record.get("doctor_name", "Dr. AyurEze"),
        regn_no="AY12345",
        contact="+91 98765 43210"
    )
    
    prescriptions = []
    med_list = record.get("prescribed_medicines", [])
    for med in med_list:
        prescriptions.append(PrescriptionItem(
            medicine=med.get("medicine_name", ""),
            dose=med.get("dose", ""),
            schedule=med.get("schedule", ""),
            duration=med.get("duration", ""),
            timing=med.get("timing", ""),
            quantity=med.get("quantity", 1),
            instructions=med.get("instructions", "")
        ))
    
    return PrescriptionRequest(
        patient=patient_info,
        doctor=doctor_info,
        prescriptions=prescriptions,
        diagnosis=record.get("diagnosis", ""),
        doctor_notes=record.get("notes", "")
    )
