import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Depends, status

from app.models import (
    SessionResponse,
    AuthenticatedChatRequest,
    ChatHistoryRequest,
    UserInfo
)

# Core imports
from app.auth import verify_token, get_current_user
from app.session_manager import session_manager
from app.database import db_manager
from app.language_utils import language_manager

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.get("/health")
async def auth_health():
    """Check auth system status"""
    return {"service": "Authentication", "status": "active"}

chat_router = APIRouter(prefix="/chat", tags=["authenticated-chat"])

@auth_router.post("/session", response_model=SessionResponse)
async def create_session(user_info: Dict[str, Any] = Depends(get_current_user)):
    """
    Exchange a valid Firebase Token (handled by get_current_user dependency)
    for a persistent Supabase Session.
    """
    try:
        # user_info is already validated and parsed by the dependency
        session_data = await session_manager.create_session(user_info)
        return SessionResponse(**session_data)

    except HTTPException:


        raise


    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create session"
        )

@auth_router.get("/user", response_model=UserInfo)
async def get_user_info_endpoint(user_info: Dict[str, Any] = Depends(get_current_user)):
    """
    Simple endpoint to echo back the user info from the token.
    """
    return UserInfo(
        id=user_info["user_id"],
        email=user_info["email"],
        name=user_info["name"],
        picture=user_info["picture"],
        email_verified=user_info["email_verified"]
    )

@auth_router.post("/logout")
async def logout(session_token: str):
    """
    Invalidate the Supabase session.
    """
    success = await session_manager.invalidate_session(session_token)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or already invalid")
    
    return {"message": "Logged out successfully"}

@chat_router.post("/message", response_model=Dict[str, Any])
async def authenticated_chat(request: AuthenticatedChatRequest):
    """
    The Main Astra Pipeline Entry Point.
    1. Validates Session (Supabase)
    2. Detects Language
    3. Retrieves RAG History (Astra Memory)
    4. Generates Response
    5. Saves to DB (Supabase)
    """
    # 1. Validate Session
    session_info = await session_manager.get_session(request.session_token)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user_id = session_info["user_id"]
    session_id = session_info["session_id"]

    # 2. Language & Context Analysis
    detected_language = request.language or language_manager.detect_language(request.message)
    is_ayurveda_related = language_manager.is_ayurveda_related(
        request.message, detected_language
    )

    # Lazy import to avoid circular dependencies during app startup
    from app.astra.routes import pipeline_instance, rag_memory_instance

    # 3. Retrieve History
    history = rag_memory_instance.get_history(user_id)

    # 4. Generate Response
    # 4. Generate Response (Pipeline already saves to Supabase)
    response_text = await pipeline_instance.process_query(
        user_id=user_id,
        message=request.message,
        history=history
    )
    
    # 5. Update Local Cache (Optional - if needed for performance)
    rag_memory_instance.add_message(user_id, "user", request.message)
    rag_memory_instance.add_message(user_id, "assistant", response_text)

    return {
        "response": response_text,
        "session_id": session_id,
        "user_id": user_id,
        "language": detected_language,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

@chat_router.post("/history", response_model=List[Dict[str, Any]])
async def get_chat_history(request: ChatHistoryRequest):
    """
    Retrieve chat history for a specific session.
    """
    # Validate session owner
    session_info = await session_manager.get_session(request.session_token)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")

    # TODO: Ensure request.session_id belongs to the user in session_info
    # (Optional additional security check, depending on your DB logic)

    return await db_manager.get_chat_history(
        session_id=request.session_id,
        limit=request.limit or 50
    )

@chat_router.get("/sessions")
async def get_user_sessions(session_token: str):
    """
    Get all active sessions for the user.
    """
    session_info = await session_manager.get_session(session_token)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")

    sessions = await db_manager.get_user_sessions(session_info["user_id"])

    return {
        "sessions": sessions,
        "total_count": len(sessions)
    }

