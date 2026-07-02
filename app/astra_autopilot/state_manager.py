"""
Astra Autopilot State Manager - Graceful Supabase fallback
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    from app.astra.db_connection import get_supabase_client
except Exception:
    get_supabase_client = lambda: None


class AutopilotStateManager:
    """
    Manages PatientCareState in Supabase.
    Falls back to in-memory dict if table is missing.
    """
    _mem: dict = {}
    _no_table: bool = False

    def __init__(self):
        self.supabase = get_supabase_client()
        self.table_name = "patient_care_states"

    def _default(self, patient_id: str) -> Dict[str, Any]:
        return {
            "patient_id": patient_id,
            "is_autopilot_enabled": False,
            "care_journey_stage": "new",
            "last_autopilot_check": None,
            "pending_autopilot_action": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_or_create_state(self, patient_id: str) -> Dict[str, Any]:
        cls = self.__class__
        if cls._no_table:
            if patient_id not in cls._mem:
                cls._mem[patient_id] = self._default(patient_id)
            return cls._mem[patient_id]

        if not self.supabase:
            cls._no_table = True
            return self.get_or_create_state(patient_id)

        try:
            r = self.supabase.table(self.table_name).select("*").eq("patient_id", patient_id).execute()
            if r.data:
                return r.data[0]
            ns = self._default(patient_id)
            ir = self.supabase.table(self.table_name).insert(ns).execute()
            return ir.data[0] if ir.data else ns
        except Exception as ex:
            errs = str(ex)
            if any(k in errs for k in ["PGRST205", "schema cache", "not find the table", "does not exist"]):
                logger.warning(f"Table {self.table_name!r} missing - using in-memory fallback")
                cls._no_table = True
                return self.get_or_create_state(patient_id)
            logger.error(f"get_or_create_state error: {ex}")
            return self._default(patient_id)

    def update_state(self, patient_id: str, updates: Dict[str, Any]) -> bool:
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        cls = self.__class__
        if cls._no_table:
            st = self.get_or_create_state(patient_id)
            st.update(updates)
            cls._mem[patient_id] = st
        # Instead of update(), we upsert to guarantee it works.
        # But we need the full object, so let's get it first
        st = self.get_or_create_state(patient_id)
        st.update(updates)
        st["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        try:
            r = self.supabase.table(self.table_name).upsert(st).execute()
            return True
        except Exception as ex:
            errs = str(ex)
            if any(k in errs for k in ["PGRST205", "schema cache", "not find the table"]):
                cls._no_table = True
                cls._mem[patient_id] = st
                return True
            logger.error(f"update_state error: {ex}")
            return False
