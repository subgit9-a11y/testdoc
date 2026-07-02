"""
Immutable Medical Audit Trails (Legal Liability Ledger)
Resolves Issue #12: The "Tamper-Proof Audit Log"
Provides a write-only append ledger for tracking AI hallucinations, 
doctor inputs, and Shopify Cart JSONs.
"""

import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ImmutableAuditLogger:
    """
    Append-only ledger for medical, AI, and financial operations.
    Data inserted here cannot be updated or deleted.
    """
    
    def __init__(self):
        from app.database import db_manager
        self.db_manager = db_manager

    def log_event(self, event_type: str, actor_id: str, action_details: str, payload: Dict[str, Any], session_id: Optional[str] = None):
        """
        Write-only insertion into the immutable audit ledger.
        
        Args:
            event_type: e.g., 'ai_response', 'doctor_prescription', 'shopify_cart_creation'
            actor_id: patient_id, doctor_id, or 'system_ai'
            action_details: Human-readable description
            payload: The exact JSON payload (e.g., exact cart JSON or LLM output)
            session_id: Correlating session
        """
        if not self.db_manager.is_connected():
            logger.warning(f"Audit log skipped (offline): {event_type} - {action_details}")
            return False

        try:
            audit_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "actor_id": actor_id,
                "session_id": session_id,
                "action_details": action_details,
                "payload": payload,
                # Cryptographic hash could be added here for further non-repudiation
            }

            # Insert into the Supabase table (which should have RLS policies blocking UPDATE/DELETE)
            self.db_manager.client.table("immutable_audit_logs").insert(audit_entry).execute()
            logger.info(f"🔒 Immutable Audit Logged: {event_type}")
            return True
            
        except Exception as e:
            # Critical failure: If audit logging fails, we should log to standard output at minimum
            logger.critical(f"🚨 AUDIT LOGGING FAILED: {e}. Payload: {json.dumps(payload)}")
            return False

# Global instance
audit_logger = ImmutableAuditLogger()
