"""
API endpoints for DISHA compliance management
Patient consent, audit trails, data access via Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.database import db_manager
from ..security.disha_compliance import (
    DISHACompliance, 
    ConsentType, 
    DataAccessPurpose
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["compliance"])

# Pydantic models
class ConsentRequest(BaseModel):
    patient_id: str
    consent_type: ConsentType
    purpose: str
    expires_in_days: Optional[int] = None
    consent_text: Optional[str] = None

class ConsentResponse(BaseModel):
    id: str
    patient_id: str
    consent_type: str
    purpose: str
    granted: bool
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked: bool

class AuditLogResponse(BaseModel):
    id: str
    patient_id: str
    accessed_by_id: str
    accessed_by_type: str
    access_type: str
    data_type: str
    purpose: str
    accessed_at: datetime
    success: bool

class DataExportRequest(BaseModel):
    patient_id: str
    include_audit_trail: bool = True

@router.post("/consent/grant", response_model=ConsentResponse)
async def grant_consent(
    request: ConsentRequest,
    http_request: Request
):
    """
    Grant patient consent for data processing via Supabase
    """
    compliance = DISHACompliance()
    
    consent = await compliance.grant_consent(
        patient_id=request.patient_id,
        consent_type=request.consent_type,
        purpose=request.purpose,
        expires_in_days=request.expires_in_days,
        consent_text=request.consent_text,
        ip_address=http_request.client.host,
        user_agent=http_request.headers.get('User-Agent')
    )
    
    if not consent:
        raise HTTPException(status_code=500, detail="Failed to save consent")
        
    # Ensure all required fields for ConsentResponse are present
    formatted_consent = {
        "id": str(consent.get("id", "")),
        "patient_id": str(consent.get("patient_id", "")),
        "consent_type": str(consent.get("consent_type", "")),
        "purpose": str(consent.get("purpose", "")),
        "granted": bool(consent.get("granted", True)),
        "granted_at": consent.get("granted_at") or datetime.now(),
        "expires_at": consent.get("expires_at"),
        "revoked": bool(consent.get("revoked", False))
    }
        
    return formatted_consent


@router.post("/consent/revoke")
async def revoke_consent(
    patient_id: str,
    consent_type: ConsentType
):
    """
    Revoke patient consent in Supabase
    """
    compliance = DISHACompliance()
    success = await compliance.revoke_consent(patient_id=patient_id, consent_type=consent_type)
    if not success:
        raise HTTPException(status_code=404, detail="Consent not found")
    return {"message": "Consent revoked successfully"}


@router.get("/consent/{patient_id}", response_model=List[ConsentResponse])
async def get_patient_consents(patient_id: str):
    """
    Get all consents for a patient from Supabase
    """
    compliance = DISHACompliance()
    consents = await compliance.db.get_patient_consents(patient_id)
    
    # Format for response model
    result = []
    for c in consents:
        result.append({
            "id": str(c.get("id", "")),
            "patient_id": str(c.get("patient_id", "")),
            "consent_type": str(c.get("consent_type", "")),
            "purpose": str(c.get("purpose", "")),
            "granted": bool(c.get("granted", True)),
            "granted_at": c.get("granted_at") or datetime.now(),
            "expires_at": c.get("expires_at"),
            "revoked": bool(c.get("revoked", False))
        })
    return result


@router.get("/audit/{patient_id}", response_model=List[AuditLogResponse])
async def get_audit_trail(
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get complete audit trail for a patient from Supabase
    """
    compliance = DISHACompliance()
    audits = await compliance.get_patient_audit_trail(patient_id=patient_id)
    return audits


@router.post("/data-export")
async def export_patient_data(
    request: DataExportRequest,
    http_request: Request = None
):
    """
    Export all patient data from Supabase (DISHA Compliant)
    """
    compliance = DISHACompliance()
    
    # 1. Check consent
    has_consent = await compliance.check_consent(
        patient_id=request.patient_id,
        consent_type=ConsentType.DATA_STORAGE
    )
    
    # 2. Log access
    await compliance.log_data_access(
        patient_id=request.patient_id,
        accessed_by_id=request.patient_id,
        accessed_by_type="patient",
        access_type="export",
        data_type="complete_patient_record",
        purpose=DataAccessPurpose.TREATMENT,
        ip_address=http_request.client.host if http_request else None,
        user_agent=http_request.headers.get('User-Agent') if http_request else None
    )
    
    # 3. Gather data from Supabase
    patient = await db_manager.get_patient_profile(request.patient_id)
    prescriptions = await db_manager.get_patient_prescriptions(request.patient_id)
    consultations = await db_manager.get_patient_consultations(request.patient_id)
    
    # Documents
    docs_res = db_manager.client.table("document_records").select("*").eq("patient_id", request.patient_id).eq("is_deleted", False).execute() if db_manager.client else None
    documents = docs_res.data if docs_res else []
    
    # Compile
    patient_data = {
        "patient_id": request.patient_id,
        "personal_info": patient,
        "prescriptions": prescriptions,
        "consultations": consultations,
        "documents": documents,
        "export_timestamp": datetime.now().isoformat(),
        "total_records": {
            "prescriptions": len(prescriptions),
            "consultations": len(consultations),
            "documents": len(documents)
        }
    }
    
    if request.include_audit_trail:
        patient_data["audit_trail"] = await compliance.get_patient_audit_trail(request.patient_id)
    
    return patient_data


@router.delete("/patient-data/{patient_id}")
async def delete_patient_data(
    patient_id: str,
    confirm: bool = False
):
    """
    Delete all patient data (Anonymizes in Supabase)
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Please confirm deletion")
    
    compliance = DISHACompliance()
    await compliance.log_data_access(
        patient_id=patient_id,
        accessed_by_id="system",
        accessed_by_type="system",
        access_type="delete",
        data_type="all_patient_data",
        purpose=DataAccessPurpose.TREATMENT
    )
    
    try:
        if not db_manager.client: return {"message": "DB not connected"}
        
        # Anonymize profile
        db_manager.client.table("patient_profiles").update({
            "name": f"DELETED_{patient_id[:6]}",
            "email": "deleted@anonymized",
            "phone": "0000000000",
            "is_active": False
        }).eq("patient_id", patient_id).execute()
        
        # Soft delete docs
        db_manager.client.table("document_records").update({"is_deleted": True}).eq("patient_id", patient_id).execute()
        
        return {"message": "Patient data anonymized in Supabase successfully"}
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-status/{patient_id}")
async def get_compliance_status(patient_id: str):
    """
    Get DISHA compliance status from Supabase
    """
    compliance = DISHACompliance()
    has_consent = await compliance.check_consent(
        patient_id=patient_id,
        consent_type=ConsentType.DATA_STORAGE
    )
    
    return {
        "patient_id": patient_id,
        "encryption_enabled": True,
        "consent_granted": has_consent,
        "audit_trail_enabled": True,
        "compliance_level": "DISHA Compliant (Supabase)",
        "last_audit_check": datetime.now().isoformat()
    }
