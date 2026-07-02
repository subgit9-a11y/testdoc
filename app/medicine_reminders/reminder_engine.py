"""
Medicine Reminder Engine (Supabase Powered)
Handles scheduling, sending, and tracking medicine reminders via Supabase.
"""

import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
import os

from app.database import db_manager
from .custom_whatsapp_client import CustomWhatsAppClient
from .prescription_analyzer import PrescriptionAnalyzer

logger = logging.getLogger(__name__)

class ReminderEngine:
    """Engine for managing medicine reminders and patient adherence using Supabase"""
    
    def __init__(self):
        # Initialize custom WhatsApp client
        try:
            self.whatsapp_client = CustomWhatsAppClient()
            logger.info("✅ Custom WhatsApp client initialized for reminders")
        except Exception as e:
            logger.error(f"WhatsApp client error: {e}")
            self.whatsapp_client = None
        
        self.prescription_analyzer = PrescriptionAnalyzer()
        
        # Default reminder times
        self.default_times = {
            'morning': time(8, 0),    # 8:00 AM
            'afternoon': time(13, 0), # 1:00 PM
            'evening': time(20, 0)    # 8:00 PM
        }
    
    async def create_medicine_schedules_from_prescription(self, prescription_id: str) -> bool:
        """Create medicine schedules from a prescription using Supabase"""
        try:
            # 1. Get prescription & medicines from Supabase (using joined query if possible)
            res = db_manager.client.table("prescription_records").select("*, prescribed_medicines(*)").eq("prescription_id", prescription_id).execute()
            if not res.data:
                logger.error(f"Prescription not found in Supabase: {prescription_id}")
                return False
            
            prescription = res.data[0]
            patient_id = prescription.get("patient_id")
            
            # 2. Get patient details from Supabase
            patient = await db_manager.get_patient_profile(patient_id)
            if not patient:
                logger.error(f"Patient profile not found: {patient_id}")
                return False
            
            # 3. Analyze medicines to extract schedules
            medicines_data = []
            for med in prescription.get("prescribed_medicines", []):
                medicines_data.append({
                    'medicine_name': med.get('medicine_name'),
                    'dose': med.get('dose'),
                    'schedule': med.get('schedule'),
                    'timing': med.get('timing'),
                    'duration': med.get('duration'),
                    'instructions': med.get('instructions')
                })
            
            if not medicines_data: return False
            
            analyzed_medicines = self.prescription_analyzer.analyze_prescribed_medicines(medicines_data)
            
            # 4. Create schedules in Supabase
            created_count = 0
            for medicine in analyzed_medicines:
                # Prepare schedule data for Supabase
                start_date = datetime.now()
                end_date = start_date + timedelta(days=medicine['duration_days'])
                
                schedule_pattern = f"{medicine['schedule'].get('morning', 0)}-{medicine['schedule'].get('afternoon', 0)}-{medicine['schedule'].get('evening', 0)}"
                
                schedule_data = {
                    "prescription_id": prescription_id,
                    "patient_id": patient_id,
                    "medicine_name": medicine['medicine_name'],
                    "dose_amount": medicine['dose_amount'],
                    "schedule_pattern": schedule_pattern,
                    "timing_type": medicine['timing_type'],
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "is_active": True,
                    "reminders_enabled": True
                }
                
                schedule_id = await db_manager.create_medicine_schedule(schedule_data)
                if schedule_id:
                    # Create actual reminders for the next 3 days
                    await self._create_reminders_in_supabase(schedule_id, schedule_data, patient_id)
                    created_count += 1
            
            return created_count > 0
            
        except Exception as e:
            logger.error(f"Error creating medicine schedules in Supabase: {e}")
            return False

    async def _create_reminders_in_supabase(self, schedule_id: int, schedule: Dict[str, Any], patient_id: str):
        """Create individual reminder instances in Supabase"""
        try:
            reminders = []
            start = datetime.fromisoformat(schedule["start_date"])
            
            for d in range(3): # Next 3 days
                curr_date = (start + timedelta(days=d)).date()
                
                # Morning reminder
                if schedule.get("morning_time"):
                    rem_time = datetime.combine(curr_date, time(8, 0)) - timedelta(minutes=30)
                    if rem_time > datetime.now():
                        reminders.append({
                            "schedule_id": schedule_id, "patient_id": patient_id,
                            "reminder_datetime": rem_time.isoformat(), "dose_datetime": datetime.combine(curr_date, time(8, 0)).isoformat(),
                            "dose_type": "morning", "status": "scheduled"
                        })
                # Afternoon
                if schedule.get("afternoon_time"):
                    rem_time = datetime.combine(curr_date, time(13, 0)) - timedelta(minutes=30)
                    if rem_time > datetime.now():
                        reminders.append({
                            "schedule_id": schedule_id, "patient_id": patient_id,
                            "reminder_datetime": rem_time.isoformat(), "dose_datetime": datetime.combine(curr_date, time(13, 0)).isoformat(),
                            "dose_type": "afternoon", "status": "scheduled"
                        })
                # Evening
                if schedule.get("evening_time"):
                    rem_time = datetime.combine(curr_date, time(20, 0)) - timedelta(minutes=30)
                    if rem_time > datetime.now():
                        reminders.append({
                            "schedule_id": schedule_id, "patient_id": patient_id,
                            "reminder_datetime": rem_time.isoformat(), "dose_datetime": datetime.combine(curr_date, time(20, 0)).isoformat(),
                            "dose_type": "evening", "status": "scheduled"
                        })
            
            if reminders:
                await db_manager.create_reminders(reminders)
                
        except Exception as e:
            logger.error(f"Error bulk creating reminders: {e}")

    async def send_pending_reminders(self) -> int:
        """Send all pending reminders using Supabase"""
        try:
            sent_count = 0
            # Get reminders from Supabase due in the next 5 minutes
            now = datetime.now()
            
            reminders = await db_manager.get_pending_reminders(now + timedelta(minutes=5))
            
            for rem in reminders:
                patient_phone = rem.get("patient_profiles", {}).get("phone")
                if not patient_phone and self.whatsapp_client: continue
                
                msg_body = f"🌿 *Medicine Reminder*\nPlease take: {rem.get('medicine_schedules', {}).get('medicine_name')}"
                
                await self.whatsapp_client.send_text_message(patient_phone, msg_body)
                
                # Update status in Supabase
                db_manager.client.table("medicine_reminders").update({"status": "sent", "whatsapp_sent": True}).eq("id", rem["id"]).execute()
                sent_count += 1
            
            return sent_count
        except Exception as e:
            logger.error(f"Error sending reminders via Supabase: {e}")
            return 0