from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Any, Dict
from app.audit_logger import audit_logger

router = APIRouter(prefix="/audit", tags=["Audit Log"])

class AuditEventRequest(BaseModel):
    event_type: str
    action_details: str
    payload: Dict[str, Any]
    session_id: str = None

@router.post("/log")
async def log_audit_event(
    event: AuditEventRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Client-side audit logging endpoint.
    Used by the frontend to stream 'doctor keystrokes' or intermediate draft saves
    into the immutable ledger without blocking UI threads.
    """
    # Use client IP or token as actor_id if auth is missing
    actor_id = request.client.host
    
    background_tasks.add_task(
        audit_logger.log_event,
        event_type=event.event_type,
        actor_id=actor_id,
        action_details=event.action_details,
        payload=event.payload,
        session_id=event.session_id
    )
    
    return {"status": "logged"}
