"""
DISHA (Digital Information Security in Healthcare Act) Compliance
Implements India's healthcare data protection requirements using Supabase
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import logging

from app.database import db_manager

logger = logging.getLogger(__name__)

class ConsentType(str, Enum):
    """Types of consent as per DISHA"""
    DATA_COLLECTION = "data_collection"
    DATA_STORAGE = "data_storage"
    DATA_PROCESSING = "data_processing"
    DATA_SHARING = "data_sharing"
    TELEMEDICINE = "telemedicine"
    PRESCRIPTION = "prescription"
    DIAGNOSTIC_TESTS = "diagnostic_tests"
    RESEARCH = "research"

class DataAccessPurpose(str, Enum):
    """Purpose of data access for audit trail"""
    TREATMENT = "treatment"
    CONSULTATION = "consultation"
    PRESCRIPTION = "prescription"
    DIAGNOSIS = "diagnosis"
    BILLING = "billing"
    RESEARCH = "research"
    ANALYTICS = "analytics"
    PATIENT_REQUEST = "patient_request"
    LEGAL_REQUIREMENT = "legal_requirement"

class DISHACompliance:
    """
    DISHA Compliance Manager (Supabase Powered)
    Handles consent, audit, and compliance requirements
    """
    
    def __init__(self, db_session=None):
        # db_session is kept for backward compatibility but ignored
        self.db = db_manager
    
    async def check_consent(
        self, 
        patient_id: str, 
        consent_type: ConsentType,
        purpose: Optional[str] = None
    ) -> bool:
        """
        Check if valid consent exists in Supabase
        """
        consent = await self.db.get_patient_consent(patient_id, consent_type.value)
        return bool(consent)
    
    async def grant_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        purpose: str,
        expires_in_days: Optional[int] = None,
        consent_text: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record patient consent in Supabase
        """
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        consent_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "consent_type": consent_type.value,
            "purpose": purpose,
            "granted": True,
            "granted_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "consent_text": consent_text,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "revoked": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        success = await self.db.save_patient_consent(consent_data)
        return consent_data if success else {}
    
    async def revoke_consent(
        self,
        patient_id: str,
        consent_type: ConsentType
    ) -> bool:
        """
        Revoke patient consent in Supabase
        """
        if not self.db.client: return False
        try:
            res = self.db.client.table("patient_consents").update({
                "revoked": True,
                "revoked_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).eq("patient_id", patient_id).eq("consent_type", consent_type.value).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Revoke consent error: {e}")
            return False
    
    async def log_data_access(
        self,
        patient_id: str,
        accessed_by_id: str,
        accessed_by_type: str,
        access_type: str,
        data_type: str,
        purpose: DataAccessPurpose,
        accessed_fields: Optional[List[str]] = None,
        consent_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log all health data access in Supabase for audit trail
        """
        audit_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "accessed_by_id": accessed_by_id,
            "accessed_by_type": accessed_by_type,
            "access_type": access_type,
            "data_type": data_type,
            "purpose": purpose.value,
            "consent_id": consent_id,
            "accessed_fields": accessed_fields or [],
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "failure_reason": failure_reason,
            "accessed_at": datetime.now().isoformat()
        }
        
        logged = await self.db.create_audit_log(audit_data)
        return audit_data if logged else {}
    
    async def get_patient_audit_trail(
        self,
        patient_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get complete audit trail from Supabase
        """
        return await self.db.get_audit_trail(patient_id)
    
    async def anonymize_data(self, patient_data: Dict) -> Dict:
        """
        Anonymize patient data for research/analytics
        Removes all PII as per DISHA requirements
        """
        anonymized = patient_data.copy()
        pii_fields = ['name', 'phone', 'email', 'address', 'patient_id', 'id']
        for field in pii_fields:
            if field in anonymized: anonymized[field] = "[ANONYMIZED]"
        return anonymized

    async def log_data_breach(
        self,
        breach_type: str,
        severity: str,
        affected_patients: List[str],
        affected_data_types: List[str],
        description: str,
        impact_assessment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log data breach in Supabase
        """
        breach_data = {
            "id": str(uuid.uuid4()),
            "breach_type": breach_type,
            "severity": severity,
            "affected_patients": affected_patients,
            "affected_data_types": affected_data_types,
            "breach_detected_at": datetime.now().isoformat(),
            "description": description,
            "impact_assessment": impact_assessment,
            "created_at": datetime.now().isoformat()
        }
        
        if self.db.client:
            try:
                self.db.client.table("data_breach_logs").insert(breach_data).execute()
            except Exception as e:
                logger.error(f"Log breach error: {e}")
        
        return breach_data
