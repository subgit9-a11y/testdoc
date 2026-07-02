"""
Simplified Authentication Routes for Frontend Integration (Supabase Powered)
Handles JWT validation and session management for React/Vue/Angular frontends via Supabase
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.database import db_manager
from app.session_manager import session_manager
from app.auth import verify_token
from app.language_utils import language_manager

logger = logging.getLogger(__name__)

# Create simplified router for frontend integration
simple_auth_router = APIRouter(prefix="/api", tags=["frontend-auth"])

@simple_auth_router.post("/auth/validate-token")
async def validate_token(request: Request):
    """Validate JWT token from frontend and return user info"""
    try:
        # Get JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Authorization header with Bearer token required"
            )
        
        # Extract and verify the JWT token
        token = auth_header.split(" ")[1]
        user_info = verify_token(token)
        
        return {
            "valid": True,
            "user": {
                "id": user_info.get("sub"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "email_verified": user_info.get("email_verified", False)
            }
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return {
            "valid": False,
            "error": "Invalid or expired token"
        }

@simple_auth_router.post("/auth/create-session")
async def create_backend_session(
    request: Request
):
    """Create a backend session after frontend Firebase authentication via Supabase"""
    try:
        # Get JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Authorization header with Bearer token required"
            )
        
        # Extract and verify the JWT token
        token = auth_header.split(" ")[1]
        user_info = verify_token(token)
        
        # Create user info dict from JWT payload
        user_data = {
            "user_id": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "email_verified": user_info.get("email_verified", False)
        }
        
        # Create session in Supabase
        session_data = await session_manager.create_session(user_data)
        
        return {
            "success": True,
            "session_token": session_data["session_token"],
            "session_id": session_data["session_id"],
            "user": session_data["user"],
            "expires_at": session_data["expires_at"]
        }
        
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create session"
        )

@simple_auth_router.post("/chat/send")
async def send_chat_message(
    request: Request,
    session_token: str
):
    """Send a chat message with Supabase session authentication"""
    try:
        body = await request.json()
        
        # Verify session via Supabase
        session_info = await session_manager.get_session(session_token)
        if not session_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired session"
            )
        
        user_id = session_info["user_id"]
        session_id = session_info["session_id"]
        message = body.get("message", "")
        
        if not message:
            raise HTTPException(
                status_code=400,
                detail="Message is required"
            )
        
        # Detect language
        detected_language = body.get("language") or language_manager.detect_language(message)
        is_ayurveda_related = language_manager.is_ayurveda_related(message, detected_language)
        
        # Get global model
        from main_enhanced import model_inference
        if not model_inference or not model_inference.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="Astra is preparing. Please wait."
            )
        
        response_text = await model_inference.generate_response(
            prompt=message,
            language=detected_language,
            max_length=body.get("max_length", 512),
            temperature=body.get("temperature", 0.7)
        )
        
        # Prepare chat record for Supabase
        chat_data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": message,
            "assistant_response": response_text,
            "detected_language": detected_language,
            "language_name": language_manager.get_language_name(detected_language),
            "is_ayurveda_related": is_ayurveda_related,
            "model_name": "Astra Llama-3-Ayurveda",
            "prompt_tokens": len(message.split()),
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(message.split()) + len(response_text.split()),
            "chat_metadata": body.get("metadata", {})
        }
        
        # Save to Supabase
        chat_entry = await db_manager.save_chat_message(chat_data)
        
        return {
            "success": True,
            "response": response_text,
            "session_id": session_id,
            "user_id": user_id,
            "message_id": str(chat_entry.get("id"))
        }
        
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )

@simple_auth_router.get("/chat/history")
async def get_chat_history(
    session_token: str,
    session_id: Optional[str] = None,
    limit: int = 50
):
    """Get chat history from Supabase for authenticated user"""
    try:
        # Verify session
        session_info = await session_manager.get_session(session_token)
        if not session_info:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_id = session_info["user_id"]
        
        # Get history from Supabase
        chat_history = await db_manager.get_user_chat_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
        
        return {
            "success": True,
            "messages": chat_history,
            "total_count": len(chat_history)
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@simple_auth_router.post("/auth/logout")
async def logout_session(
    session_token: str
):
    """Logout and invalidate Supabase session"""
    try:
        success = await session_manager.invalidate_session(session_token)
        return {"success": success, "message": "Logged out successfully"}
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Failed to logout: {e}")
        return {"success": False, "message": "Logout failed"}
