"""
Advanced Escalation System (Supabase Powered)
Handles missed doses, family notifications, and emergency alerts via Supabase.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.database import db_manager
from app.multilang.language_manager import language_manager
from app.medicine_reminders.custom_whatsapp_client import CustomWhatsAppClient

logger = logging.getLogger(__name__)

class EscalationSystem:
    """Advanced escalation system for medicine reminders using Supabase"""
    
    def __init__(self):
        self.whatsapp_client = CustomWhatsAppClient()
        self.escalation_rules = {
            'emergency_threshold_hours': 24,
            'family_notification_delay': 2
        }
    
    async def check_missed_doses(self) -> Dict[str, Any]:
        """Check for missed doses and trigger escalations via Supabase"""
        if not db_manager.is_connected() or not db_manager.client:
            return {'error': 'No DB'}
            
        try:
            now = datetime.now()
            overdue_threshold = now - timedelta(minutes=30)
            
            # Query pending reminders past threshold
            res = db_manager.client.table("medicine_reminders")\
                .select("*")\
                .lt("reminder_datetime", overdue_threshold.isoformat())\
                .eq("status", "pending")\
                .lt("escalation_level", 3)\
                .execute()
            
            overdue = res.data or []
            results = {
                'overdue_count': len(overdue),
                'escalations': 0,
                'family_notified': 0
            }
            
            for rem in overdue:
                esc_res = await self._escalate_reminder(rem)
                if esc_res.get('escalated'): results['escalations'] += 1
                if esc_res.get('family_notified'): results['family_notified'] += 1
                
            return results
        except Exception as e:
            logger.error(f"Escalation check error: {e}")
            return {'error': str(e)}

    async def _escalate_reminder(self, reminder: Dict) -> Dict[str, bool]:
        """Escalate a specific missed reminder using Supabase data"""
        try:
            now = datetime.now()
            rem_id = reminder.get('id')
            sched_id = reminder.get('schedule_id')
            
            # Fetch schedule
            sched_res = db_manager.client.table("medicine_schedules").select("*").eq("id", sched_id).execute()
            if not sched_res.data: return {'escalated': False}
            schedule = sched_res.data[0]
            
            # Calculate overdue
            rem_time = datetime.fromisoformat(reminder['reminder_datetime'].replace('Z', '+00:00'))
            hours_overdue = (now - rem_time).total_seconds() / 3600
            
            lvl = reminder.get('escalation_level', 0)
            res = {'escalated': True, 'family_notified': False}
            
            # Logic
            if hours_overdue >= 24:
                # Emergency
                await self._send_notification(schedule, "emergency_missed")
                db_manager.client.table("medicine_reminders").update({
                    "escalation_level": 5, "status": "missed"
                }).eq("id", rem_id).execute()
            elif schedule.get('is_critical') and hours_overdue >= 2:
                # Family
                await self._send_notification(schedule, "family_notification")
                db_manager.client.table("medicine_reminders").update({
                    "escalation_level": 4
                }).eq("id", rem_id).execute()
                res['family_notified'] = True
            else:
                # Regular
                await self._send_notification(schedule, "escalation_reminder")
                db_manager.client.table("medicine_reminders").update({
                    "escalation_level": lvl + 1
                }).eq("id", rem_id).execute()
            
            return res
        except Exception as e:
            logger.error(f"Escalation error for {reminder.get('id')}: {e}")
            return {'escalated': False}

    async def _send_notification(self, schedule: Dict, type: str):
        """Send WhatsApp notification via custom client"""
        phone = schedule.get('patient_phone')
        name = schedule.get('patient_name')
        med = schedule.get('medicine_name')
        
        if type == "family_notification":
            phone = schedule.get('family_contact_phone') or phone
            msg = f"Alert: {name} has missed a critical dose of {med}. Please check on them."
        else:
            msg = f"Reminder: {name}, you have a missed dose of {med}. Please take it urgently."
            
        await self.whatsapp_client.send_notification(phone, msg)

# Global instance
escalation_system = EscalationSystem()

# Global escalation system instance
escalation_system = EscalationSystem()