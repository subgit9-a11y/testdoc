import logging
import asyncio
from app.autopilot_engine import AutopilotEngine

logger = logging.getLogger(__name__)

async def run_daily_autopilot_check():
    """
    Scheduled task to run the Autopilot Engine for all enabled patients via Supabase.
    """
    logger.info("🤖 Starting Daily Autopilot Check (Supabase Only)...")
    
    try:
        # AutopilotEngine no longer needs a SQL DB session
        engine = AutopilotEngine()
        
        # Get Supabase client from state manager
        supabase = engine.state_manager.supabase
        if not supabase:
            logger.error("Supabase not connected, skipping autopilot check")
            return

        # Get enabled patients from Supabase
        res = supabase.table("patient_care_states").select("patient_id").eq("is_autopilot_enabled", True).execute()
        enabled_patients = [r["patient_id"] for r in res.data] if res.data else []
        
        logger.info(f"Found {len(enabled_patients)} patients with Autopilot enabled.")
        
        for patient_id in enabled_patients:
            try:
                # evaluate_patient is synchronous for now but uses Supabase
                result = engine.evaluate_patient(patient_id)
                
                if result.get('status') == 'action_prepared':
                    action_type = result.get('action', {}).get('type')
                    logger.info(f"✨ ACTIONS PREPARED for {patient_id}: {action_type}")
                
            except Exception as e:
                logger.error(f"Error evaluating patient {patient_id}: {e}")
                
    except Exception as e:
        logger.error(f"Global Autopilot Scheduler Error: {e}")
        
    logger.info("Daily Autopilot Check Completed.")
