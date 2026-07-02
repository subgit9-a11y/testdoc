"""
Supabase-based Medicine Reminder Service
Points to the central db_manager for consistency.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.database import db_manager
import uuid

logger = logging.getLogger(__name__)

class SupabaseReminderService:
    """Medicine reminder service using unified db_manager"""
    
    def __init__(self):
        self.enabled = db_manager.is_connected()
        if self.enabled:
            logger.info("✅ Supabase Reminder Service initialized via db_manager")
    
    def create_reminder(
        self,
        patient_id: str,
        patient_name: str,
        patient_phone: str,
        medicine_name: str,
        dosage: str,
        frequency: str,
        times: List[str],
        start_date: str,
        end_date: str,
        instructions: Optional[str] = None,
        enable_whatsapp: bool = True
    ) -> Dict[str, Any]:
        """Create a new medicine reminder in Supabase"""
        if not db_manager.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            reminder_id = str(uuid.uuid4())
            # Prepare schedule data for the new schema
            schedule_data = {
                "prescription_id": f"EXT-{reminder_id[:8].upper()}",
                "patient_id": patient_id,
                "medicine_name": medicine_name,
                "dose_amount": dosage,
                "schedule_pattern": "-".join(["1" if t else "0" for t in times]),
                "timing_type": instructions or "daily",
                "duration_days": 30,
                "start_date": start_date,
                "end_date": end_date,
                "is_active": True,
                "reminders_enabled": enable_whatsapp
            }
            
            # Map times to morning/afternoon/evening if possible
            # Simplified for now: just store as metadata or use medicine_reminders table directly
            
            reminder_record = {
                "id": reminder_id,
                "patient_id": patient_id,
                "medicine_name": medicine_name,
                "dosage": dosage,
                "frequency": frequency,
                "reminder_times": times,
                "start_date": start_date,
                "end_date": end_date,
                "is_active": True,
                "enable_whatsapp": enable_whatsapp,
                "created_at": datetime.now().isoformat()
            }
            
            res = db_manager.client.table('medicine_reminders').insert(reminder_record).execute()
            
            return {
                "success": True,
                "reminder_id": reminder_id,
                "message": "Reminder created successfully",
                "data": reminder_record
            }
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            raise Exception(f"Failed to create reminder: {str(e)}")

    def get_patient_reminders(self, patient_id: str) -> List[Dict[str, Any]]:
        if not db_manager.is_connected(): return []
        try:
            res = db_manager.client.table('medicine_reminders').select('*').eq('patient_id', patient_id).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error fetching reminders: {e}")
            return []

# Global instance
supabase_reminder_service = SupabaseReminderService()
