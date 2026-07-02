"""
Supabase database integration for Astra
Manages chat, family, ehr, and prescription data
"""

import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase database operations"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.info(f"Supabase connection skipped (running in offline mode): {e}")
                self.client = None
        else:
            logger.info("Supabase credentials not found, running without database")
    
    def is_connected(self) -> bool:
        """Check if Supabase client is available"""
        return self.client is not None

    # --- CHAT SYSTEM ---
    async def create_chat_session(self, user_id: str, language: str = "en") -> Optional[str]:
        if not self.client: return None
        try:
            session_data = {
                "user_id": user_id,
                "language": language,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            res = self.client.table("astra_chat_sessions").insert(session_data).execute()
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            logger.error(f"Chat session error: {e}")
            return None

    async def save_chat_message(self, *args, **kwargs) -> Any:
        # Resolve chat_data if passed as dictionary (e.g. simplified_auth.py)
        chat_data = kwargs.get('chat_data')
        if not chat_data and args and isinstance(args[0], dict):
            chat_data = args[0]
            
        if not self.client: 
            return chat_data if chat_data else False
            
        try:
            if chat_data is not None:
                res = self.client.table("astra_chat_history").insert(chat_data).execute()
                return res.data[0] if res.data else chat_data
                
            # Otherwise extract arguments (e.g. auth_routes.py)
            session_id = kwargs.get('session_id') or (args[0] if len(args) > 0 else None)
            user_message = kwargs.get('user_message') or (args[1] if len(args) > 1 else None)
            assistant_response = kwargs.get('assistant_response') or (args[2] if len(args) > 2 else None)
            language = kwargs.get('language', "en")
            metadata = kwargs.get('metadata') or {}
            
            msg = {
                "session_id": session_id,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "language": language,
                "metadata": metadata,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            res = self.client.table("astra_chat_history").insert(msg).execute()
            # Update session
            if session_id:
                self.client.table("astra_chat_sessions").update({"updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", session_id).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Save message error: {e}")
            return chat_data if chat_data else False

    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            res = self.client.table("astra_chat_history").select("*").eq("session_id", session_id).order("created_at", desc=False).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get history error: {e}")
            return []

    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            res = self.client.table("astra_chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get sessions error: {e}")
            return []

    # --- FAMILY SYSTEM ---
    async def get_family_profile(self, primary_patient_id: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            res = self.client.table("family_profiles").select("*").eq("primary_patient_id", primary_patient_id).execute()
            if res.data: return res.data[0]
            new_prof = {"primary_patient_id": primary_patient_id, "name": f"Family Profile ({primary_patient_id[:8]})"}
            res = self.client.table("family_profiles").insert(new_prof).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Family profile error: {e}")
            return None

    # --- PRESCRIPTION & EHR SYSTEM ---
    async def get_patient_profile(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient profile from Supabase"""
        if not self.client: return None
        try:
            res = self.client.table("patient_profiles").select("*").eq("patient_id", patient_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Get patient profile error: {e}")
            return None

    async def get_prescription(self, prescription_id: str) -> Optional[Dict[str, Any]]:
        """Get prescription details from Supabase with medicines"""
        if not self.client: return None
        try:
            res = self.client.table("prescription_records").select("*").eq("prescription_id", prescription_id).execute()
            if not res.data: return None
            rx = res.data[0]
            med_res = self.client.table("prescribed_medicines").select("*").eq("prescription_id", prescription_id).execute()
            rx["prescribed_medicines"] = med_res.data or []
            return rx
        except Exception as e:
            logger.error(f"Get prescription error: {e}")
            return None

    async def create_prescription(self, rx_data: Dict[str, Any], medicines: List[Dict[str, Any]]) -> Optional[str]:
        if not self.client: return None
        try:
            res = self.client.table("prescription_records").insert(rx_data).execute()
            if not res.data: return None
            for med in medicines:
                med["prescription_id"] = rx_data["prescription_id"]
                self.client.table("prescribed_medicines").insert(med).execute()
            return rx_data["prescription_id"]
        except Exception as e:
            logger.error(f"Create prescription error: {e}")
            return None

    async def create_document_record(self, doc_data: Dict[str, Any]) -> bool:
        """Saves metadata about uploaded documents to 'documents' table"""
        if not self.client: return False
        try:
            # Table name is 'documents' in current Supabase schema
            res = self.client.table("documents").insert(doc_data).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Create doc record error: {e}")
            return False

    # --- CONSULTATION SYSTEM ---
    async def create_consultation(self, consult_data: Dict[str, Any]) -> Optional[str]:
        if not self.client: return None
        try:
            if "consultation_id" not in consult_data:
                consult_data["consultation_id"] = f"CONS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Use 'notes' if 'complaints' is missing in target schema
            if "complaints" in consult_data:
                consult_data["notes"] = f"Complaints: {consult_data.pop('complaints')}\n{consult_data.get('notes', '')}"
                
            res = self.client.table("consultations").insert(consult_data).execute()
            return res.data[0]["consultation_id"] if res.data else None
        except Exception as e:
            logger.error(f"Create consultation error: {e}")
            return None

    async def get_patient_consultations(self, patient_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            res = self.client.table("consultations").select("*").eq("patient_id", patient_id).order("appointment_date", desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get patient consultations error: {e}")
            return []

    async def get_patient_prescriptions(self, patient_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all prescriptions for a patient with medicines"""
        if not self.client: return []
        try:
            res = self.client.table("prescription_records").select("*, prescribed_medicines(*)").eq("patient_id", patient_id).order("prescribed_at", desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get patient prescriptions error: {e}")
            return []

    # --- PATIENT SEARCH & MANAGEMENT ---
    async def search_patients(self, search_term: str) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            # Simple OR search
            res = self.client.table("patient_profiles").select("*").or_(f"name.ilike.%{search_term}%,phone.ilike.%{search_term}%,patient_code.ilike.%{search_term}%").limit(10).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Search patients error: {e}")
            return []

    # --- DISHA COMPLIANCE ---
    async def create_audit_log(self, audit_data: Dict[str, Any]) -> bool:
        if not self.client: return False
        try:
            res = self.client.table("data_access_audits").insert(audit_data).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Create audit log error: {e}")
            return False

    async def get_audit_trail(self, patient_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            res = self.client.table("data_access_audits").select("*").eq("patient_id", patient_id).order("accessed_at", desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get audit trail error: {e}")
            return []

    async def get_patient_consent(self, patient_id: str, consent_type: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            res = self.client.table("patient_consents").select("*").eq("patient_id", patient_id).eq("consent_type", consent_type).eq("revoked", False).order("granted_at", desc=True).execute()
            if res.data:
                # Check expiry
                consent = res.data[0]
                if consent.get("expires_at"):
                    expires = datetime.fromisoformat(consent["expires_at"].replace('Z', '+00:00'))
                    if expires < datetime.now(timezone.utc):
                        return None
                return consent
            return None
        except Exception as e:
            logger.error(f"Get consent error: {e}")
            return None

    async def save_patient_consent(self, consent_data: Dict[str, Any]) -> bool:
        if not self.client: return False
        try:
            res = self.client.table("patient_consents").insert(consent_data).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Save consent error: {e}")
            return False

    # --- CHAT HISTORY ---
    # `save_chat_message` method shifted up and merged for both dict & kwargs formats

    async def get_user_chat_history(self, user_id: str, session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            query = self.client.table("astra_chat_history").select("*").eq("user_id", user_id)
            if session_id:
                query = query.eq("session_id", session_id)
            res = query.order("created_at", desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get chat history error: {e}")
            return []

    # --- MEDICINE REMINDERS ---
    async def create_medicine_schedule(self, schedule_data: Dict[str, Any]) -> Optional[int]:
        if not self.client: return None
        try:
            res = self.client.table("medicine_schedules").insert(schedule_data).execute()
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            logger.error(f"Create schedule error: {e}")
            return None

    async def create_reminders(self, reminders: List[Dict[str, Any]]) -> bool:
        if not self.client: return False
        try:
            res = self.client.table("medicine_reminders").insert(reminders).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Bulk reminders error: {e}")
            return False

    async def get_pending_reminders(self, before_time: datetime) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            res = self.client.table("medicine_reminders").select("*, medicine_schedules(*), patient_profiles(*)").eq("status", "scheduled").lte("reminder_datetime", before_time.isoformat()).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Get pending reminders error: {e}")
            return []

    # --- USER & SESSION MANAGEMENT ---
    async def upsert_user(self, user_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            data = {
                "id": user_info["user_id"], "email": user_info.get("email"),
                "name": user_info.get("name"), "picture": user_info.get("picture"),
                "email_verified": user_info.get("email_verified", False),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            res = self.client.table("astra_users").upsert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Upsert user error: {e}")
            return None

    async def create_user_session(self, user_id: str, token: str, expires: datetime = None) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            data = {
                "user_id": user_id, "session_token": token,
                "expires_at": expires.isoformat() if expires else None,
                "is_active": True, "created_at": datetime.now(timezone.utc).isoformat()
            }
            res = self.client.table("astra_sessions").insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Create user session error: {e}")
            return None

    async def get_user_session(self, token: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            res = self.client.table("astra_sessions").select("*, astra_users(*)").eq("session_token", token).eq("is_active", True).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Get session error: {e}")
            return None

    # --- ASTRA FILL SYSTEM ---
    async def save_astra_fill_extraction(self, extraction_id: str, user_id: str, data: Dict[str, Any]) -> bool:
        if not self.client: return False
        try:
            record = {
                "id": extraction_id,
                "user_id": user_id,
                "data": data,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            res = self.client.table("astra_fill_extractions").insert(record).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Save astra fill extraction error: {e}")
            return False

    async def get_astra_fill_extraction(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            res = self.client.table("astra_fill_extractions").select("*").eq("id", extraction_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Get astra fill extraction error: {e}")
            return None

    async def update_astra_fill_status(self, extraction_id: str, status: str) -> bool:
        if not self.client: return False
        try:
            res = self.client.table("astra_fill_extractions").update({"status": status}).eq("id", extraction_id).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Update astra fill status error: {e}")
            return False


# Global instance
db_manager = SupabaseManager()