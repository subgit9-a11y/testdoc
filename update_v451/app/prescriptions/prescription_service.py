"""
Prescription Service
Handles CRUD operations for prescriptions using Supabase REST API
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import uuid

logger = logging.getLogger(__name__)

class PrescriptionService:
    """Prescription service using consolidated Supabase schema"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            self.supabase = None
            self.enabled = False
            return
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
            self.enabled = False
    
    async def create_prescription(
        self,
        patient_id: str,
        doctor_id: Optional[str],
        diagnosis: str,
        medicines: List[Dict],
        symptoms: Optional[List[str]] = None,
        lifestyle_advice: Optional[str] = None,
        follow_up_date: Optional[str] = None,
        consultation_id: Optional[str] = None,
        status: str = "pending_review"
    ) -> Dict[str, Any]:
        """Create a new prescription (Consolidated Schema)"""
        if not self.enabled or not self.supabase:
            raise Exception("Prescription service not available")
        
        try:
            import hashlib
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # Use a safe slice or cast if needed for linter
            diag_slice = str(diagnosis)[:10]
            raw_id = f"{patient_id}-{timestamp}-{diag_slice}"
            prescription_id = f"PRES-{hashlib.md5(raw_id.encode()).hexdigest()[:8].upper()}"
            
            rx_data = {
                "prescription_id": prescription_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "consultation_id": consultation_id,
                "diagnosis": diagnosis,
                "symptoms": symptoms or [],
                "lifestyle_advice": lifestyle_advice,
                "follow_up_date": follow_up_date,
                "status": status,
                "prescribed_at": datetime.now().isoformat(),
            }
            
            # 1. Insert Record (Defensive: remove columns if they don't exist in Supabase yet)
            try:
                self.supabase.table('prescription_records').insert(rx_data).execute()
            except Exception as e:
                # Handle common Supabase schema mismatch errors
                error_str = str(e)
                if "follow_up_date" in error_str or "lifestyle_advice" in error_str or "symptoms" in error_str:
                    logger.warning(f"⚠️ Initial insert failed (likely missing columns): {error_str}")
                    # Remove offending columns and retry
                    safe_rx_data = rx_data.copy()
                    for col in ["follow_up_date", "lifestyle_advice", "symptoms"]:
                        if col in safe_rx_data:
                            del safe_rx_data[col]
                    self.supabase.table('prescription_records').insert(safe_rx_data).execute()
                else:
                    raise e
            
            # 2. Insert Medicines
            for med in medicines:
                med_record = {
                    "prescription_id": prescription_id,
                    "medicine_name": med.get('name', med.get('medicine_name', med.get('medicine', 'Unknown'))),
                    "dose": med.get('dosage', med.get('dose', '1')),
                    "schedule": med.get('frequency', med.get('schedule', '1-0-1')),
                    "timing": med.get('timing', 'After Meals'),
                    "duration": str(med.get('duration_days', med.get('duration', '7'))) + " days" if isinstance(med.get('duration_days'), int) else str(med.get('duration', '7 days')),
                    "instructions": med.get('instructions', ''),
                    "shopify_variant_id": med.get('shopify_variant_id') # Added for ecosystem interlink
                }
                # Defensive: Try to insert, log if column missing
                try:
                    self.supabase.table('prescribed_medicines').insert(med_record).execute()
                except Exception as med_err:
                    logger.warning(f"⚠️ Could not save shopify_variant_id (column might be missing): {med_err}")
                    # Fallback: remove it and try again
                    if "shopify_variant_id" in med_record:
                        del med_record["shopify_variant_id"]
                        self.supabase.table('prescribed_medicines').insert(med_record).execute()
            
            logger.info(f"✅ Prescription {prescription_id} saved to consolidated tables")
            
            return {
                "success": True,
                "prescription_id": prescription_id,
                "data": rx_data
            }
            
        except Exception as e:
            logger.error(f"Error creating prescription: {e}")
            raise
    
    async def get_prescription(self, prescription_id: str) -> Dict[str, Any]:
        """Get prescription with medicines joined"""
        if not self.enabled or not self.supabase:
            raise Exception("Prescription service not available")
        
        try:
            res = self.supabase.table('prescription_records').select("*, prescribed_medicines(*)").eq(
                'prescription_id', prescription_id
            ).execute()
            
            if res.data:
                return {"success": True, "data": res.data[0]}
            return {"success": False, "error": "Prescription not found"}
                
        except Exception as e:
            logger.error(f"Error getting prescription: {e}")
            raise
    
    async def get_patient_prescriptions(
        self,
        patient_id: str,
        limit: int = 50,
        active_only: bool = False
    ) -> Dict[str, Any]:
        """Get all prescriptions for a patient"""
        if not self.enabled or not self.supabase:
            raise Exception("Prescription service not available")
        
        try:
            query = self.supabase.table('prescription_records').select("*, prescribed_medicines(*)").eq(
                'patient_id', patient_id
            )
            
            if active_only:
                query = query.eq('status', 'active')
            
            res = query.order('prescribed_at', desc=True).limit(limit).execute()
            
            return {
                "success": True,
                "patient_id": patient_id,
                "count": len(res.data),
                "prescriptions": res.data
            }
        except Exception as e:
            logger.error(f"Error getting patient prescriptions: {e}")
            raise
    
    async def update_prescription(self, prescription_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update prescription metadata"""
        if not self.enabled or not self.supabase:
            raise Exception("Prescription service not available")
        
        try:
            res = self.supabase.table('prescription_records').update(updates).eq(
                'prescription_id', prescription_id
            ).execute()
            return {"success": True, "data": res.data[0] if res.data else None}
        except Exception as e:
            logger.error(f"Error updating prescription: {e}")
            raise
    
    async def delete_prescription(self, prescription_id: str) -> Dict[str, Any]:
        """Soft delete prescription"""
        if not self.enabled or not self.supabase:
            raise Exception("Prescription service not available")
        
        try:
            self.supabase.table('prescription_records').update({
                'status': 'deleted'
            }).eq('prescription_id', prescription_id).execute()
            return {"success": True, "message": "Prescription deactivated"}
        except Exception as e:
            logger.error(f"Error deleting prescription: {e}")
            raise

# Global instance
prescription_service = PrescriptionService()
