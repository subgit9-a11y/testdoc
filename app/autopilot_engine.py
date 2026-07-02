import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from app.astra_autopilot.state_manager import AutopilotStateManager

logger = logging.getLogger(__name__)

class AutopilotEngine:
    """
    Astra Autopilot™ Engine (Supabase Powered)
    
    1. OBSERVATION: Reads events from Supabase.
    2. DECISION: Evaluates logic based on Supabase state.
    3. PREPARATION: Writes drafts to Supabase state.
    """

    def __init__(self, db=None):
        # db is kept for compatibility but ignored
        self.state_manager = AutopilotStateManager() # Supabase Manager
        self.supabase = self.state_manager.supabase

    def evaluate_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Main entry point. Runs the O-D-P loop for a single patient.
        """
        logger.info(f"Autopilot: Evaluating patient {patient_id}")
        
        # 1. OBSERVATION FRAME (Load from Supabase)
        state = self.state_manager.get_or_create_state(patient_id)
        if not state:
            return {"status": "error", "reason": "state_fetch_failed"}

        if not state.get('is_autopilot_enabled', False):
            logger.info(f"Autopilot: Disabled for {patient_id}")
            return {"status": "skipped", "reason": "disabled"}

        # Refresh state from Supabase events (Consultations/Prescriptions)
        updated_state = self._refresh_observation(state)
        
        # 2. DECISION LAYER
        # A. Follow-up Check
        decision = self._check_followup_needed(updated_state)
        if decision:
             return self._prepare_action(patient_id, decision)
             
        # B. Refill Check
        decision = self._check_refill_needed(updated_state)
        if decision:
            return self._prepare_action(patient_id, decision)

        # C. Care Gap Check
        decision = self._check_care_gap(updated_state)
        if decision:
            return self._prepare_action(patient_id, decision)
            
        # Update last check time
        self.state_manager.update_state(patient_id, {
            "last_autopilot_check": datetime.now(timezone.utc).isoformat()
        })
        
        return {"status": "no_action_needed"}

    def _refresh_observation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Syncs the Supabase State with the latest Supabase events.
        """
        patient_id = state['patient_id']
        if not self.supabase: return state
        
        updates = {}
        
        try:
            # Get last completed consultation from Supabase
            res = self.supabase.table("consultations").select("*").eq("patient_id", patient_id).eq("status", "completed").order("appointment_date", desc=True).limit(1).execute()
            
            if res.data:
                last_consult = res.data[0]
                consult_date_str = last_consult.get("appointment_date")
                if consult_date_str:
                    consult_date = datetime.fromisoformat(consult_date_str.replace('Z', '+00:00'))
                    
                    if not state.get('next_followup_window_start') or \
                       state.get('last_consultation_id') != last_consult['consultation_id']:
                         
                         updates['last_consultation_date'] = consult_date.isoformat()
                         updates['last_consultation_id'] = last_consult['consultation_id']
                         
                         # Default logic: 15 days later
                         start_date = consult_date + timedelta(days=15)
                         updates['next_followup_window_start'] = start_date.isoformat()
                         updates['next_followup_window_end'] = (start_date + timedelta(days=7)).isoformat()

            # Get active prescription from Supabase
            res_rx = self.supabase.table("prescription_records").select("*").eq("patient_id", patient_id).order("prescribed_at", desc=True).limit(1).execute()

            if res_rx.data:
                last_rx = res_rx.data[0]
                if state.get('active_prescription_id') != last_rx['prescription_id']:
                    updates['active_prescription_id'] = last_rx['prescription_id']
                    
                    prescribed_at_str = last_rx.get('prescribed_at')
                    if prescribed_at_str:
                        prescribed_at = datetime.fromisoformat(prescribed_at_str.replace('Z', '+00:00'))
                        # Assume 30 days if not calculated
                        end_date = prescribed_at + timedelta(days=30)
                        updates['medicine_end_date'] = end_date.isoformat()
            
            if updates:
                self.state_manager.update_state(patient_id, updates)
                state.update(updates)
        except Exception as e:
            logger.error(f"Refresh observation error: {e}")
            
        return state

    # --- DECISION LOGIC ---

    def _check_followup_needed(self, state: Dict[str, Any]) -> Optional[Dict]:
        """ Capability A: Follow-up Orchestration """
        if not state.get('last_consultation_date') or not state.get('next_followup_window_start'):
            return None
            
        now = datetime.now(timezone.utc)
        try:
            start_window = datetime.fromisoformat(state['next_followup_window_start'].replace('Z', '+00:00'))
            if start_window.tzinfo is None:
                start_window = start_window.replace(tzinfo=timezone.utc)
            
            if start_window <= now:
                pending = state.get('pending_autopilot_action')
                if pending and pending.get('type') == 'followup_draft':
                    return None # Already prepared
                
                return {
                    "type": "followup_draft",
                    "reason": "followup_window_open",
                    "details": {
                        "suggested_date": state['next_followup_window_start'],
                        "doctor_id": "PREVIOUS_DOCTOR"
                    }
                }
        except Exception as e:
            logger.error(f"Check followup needed error: {e}")
            
        return None

    def _check_refill_needed(self, state: Dict[str, Any]) -> Optional[Dict]:
        """ Capability B: Medicine Refill Intelligence """
        if not state.get('medicine_end_date'):
            return None
            
        now = datetime.now(timezone.utc)
        try:
            end_date = datetime.fromisoformat(state['medicine_end_date'].replace('Z', '+00:00'))
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
                
            days_left = (end_date - now).days
            
            if 0 < days_left <= 5:
                 pending = state.get('pending_autopilot_action')
                 if pending and pending.get('type') == 'refill_draft':
                    return None

                 return {
                    "type": "refill_draft",
                    "reason": "medicine_running_low",
                    "details": {
                        "refill_date": state['medicine_end_date'],
                        "prescription_id": state['active_prescription_id']
                    }
                }
        except Exception as e:
            logger.error(f"Check refill needed error: {e}")
            
        return None

    def _check_care_gap(self, state: Dict[str, Any]) -> Optional[Dict]:
        """ Capability C: Care Continuity """
        return None

    # --- PREPARATION LAYER ---

    def _prepare_action(self, patient_id: str, decision: Dict) -> Dict:
        """ Creates the 'Draft' in Supabase state. """
        logger.info(f"Autopilot: Preparing action {decision['type']} for {patient_id}")
        
        action_payload = {
            "type": decision['type'],
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "payload": decision['details'],
            "status": "waiting_for_user"
        }
        
        success = self.state_manager.update_state(patient_id, {
            "pending_autopilot_action": action_payload
        })
        
        if success:
            return {
                "status": "action_prepared",
                "action": action_payload
            }
        else:
             return {"status": "error", "reason": "state_update_failed"}
