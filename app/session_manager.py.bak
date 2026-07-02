"""
Session Management for Astra - Ayurvedic Wellness Assistant
Handles persistent sessions and session tokens.

FALLBACK MODE: When Supabase tables (astra_users / astra_sessions) are
missing the manager automatically falls back to an in-memory store so
POST /api/v1/auth/session always returns 200 instead of 500.
Create the tables via the Supabase Dashboard SQL to enable persistence:
  https://supabase.com/dashboard/project/ykewayjfdanhqtqpziwt/sql
"""

import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from app.database import db_manager
import logging

logger = logging.getLogger(__name__)

# ── In-memory fallback store ──────────────────────────────────────────────────
# Used when Supabase tables are missing. Survives as long as the process runs.
_mem_sessions: Dict[str, Dict[str, Any]] = {}


class SessionManager:
    """Manages user sessions using Supabase (with in-memory fallback)."""

    def __init__(self, session_duration_hours: int = 24 * 7):  # 1-week default
        self.session_duration_hours = session_duration_hours

    # ── helpers ───────────────────────────────────────────────────────────────

    def generate_session_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _is_missing_table_error(self, exc: Exception) -> bool:
        """Return True when the exception is caused by a missing Supabase table or uninitialized client."""
        msg = str(exc)
        if not db_manager.client:
            return True
        return (
            "PGRST205" in msg or 
            "schema cache" in msg or 
            "Failed to upsert user" in msg or 
            "Failed to create session" in msg or
            "not initialized" in msg.lower()
        )

    # ── mem-store helpers ─────────────────────────────────────────────────────

    def _mem_create(self, user_info: Dict[str, Any], session_token: str,
                    session_id: str, expires_at: datetime) -> Dict[str, Any]:
        record = {
            "session_id":    session_id,
            "user_id":       user_info["user_id"],
            "user":          user_info,
            "expires_at":    expires_at.isoformat(),
            "created_at":    datetime.now(timezone.utc).isoformat(),
            "last_accessed": datetime.now(timezone.utc).isoformat(),
            "is_active":     True,
            "_source":       "memory",
        }
        _mem_sessions[session_token] = record
        logger.info(f"[MEM] Created in-memory session {session_id} for {user_info.get('email')}")
        return record

    def _mem_get(self, session_token: str) -> Optional[Dict[str, Any]]:
        record = _mem_sessions.get(session_token)
        if not record or not record.get("is_active"):
            return None
        # expiry check
        expires_str = record.get("expires_at", "")
        if expires_str:
            try:
                expires_at = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > expires_at:
                    record["is_active"] = False
                    return None
            except Exception:
                pass
        record["last_accessed"] = datetime.now(timezone.utc).isoformat()
        return record

    # ── public API ────────────────────────────────────────────────────────────

    async def create_session(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new session after Firebase auth.
        Tries Supabase first; falls back to in-memory if tables are missing.
        """
        session_token = self.generate_session_token()
        session_id    = str(uuid.uuid4())
        expires_at    = datetime.now(timezone.utc) + timedelta(hours=self.session_duration_hours)

        # ── Try Supabase ──────────────────────────────────────────────────────
        try:
            user = await db_manager.upsert_user(user_info)
            if not user:
                raise Exception("Failed to upsert user in Supabase")

            session = await db_manager.create_user_session(
                user["id"], session_token, expires_at
            )
            if not session:
                raise Exception("Failed to create session row in Supabase")

            logger.info(f"[SUPABASE] Created session for user {user['id']}")
            return {
                "session_token": session_token,
                "session_id":    str(session.get("id", session_id)),
                "user": {
                    "id":             user["id"],
                    "email":          user.get("email"),
                    "name":           user.get("name"),
                    "picture":        user.get("picture"),
                    "email_verified": user.get("email_verified", False),
                },
                "expires_at": expires_at.isoformat(),
                "_source":    "supabase",
            }

        except Exception as e:
            if self._is_missing_table_error(e):
                logger.warning(
                    f"[FALLBACK] Supabase tables missing ({e}). "
                    "Falling back to in-memory session store. "
                    "Run the SQL script in the Supabase Dashboard to fix permanently."
                )
                record = self._mem_create(user_info, session_token, session_id, expires_at)
                return {
                    "session_token": session_token,
                    "session_id":    record["session_id"],
                    "user": {
                        "id":             user_info["user_id"],
                        "email":          user_info.get("email"),
                        "name":           user_info.get("name"),
                        "picture":        user_info.get("picture"),
                        "email_verified": user_info.get("email_verified", False),
                    },
                    "expires_at": expires_at.isoformat(),
                    "_source":    "memory",
                }
            # A different, unexpected error — still log & re-raise
            logger.error(f"[ERROR] Session creation failed: {e}")
            raise

    async def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session info — tries Supabase first, then in-memory fallback."""
        # ── Supabase path ─────────────────────────────────────────────────────
        try:
            session = await db_manager.get_user_session(session_token)
            if session:
                expires_at_str = session.get("expires_at")
                if expires_at_str:
                    try:
                        expires_at = datetime.fromisoformat(
                            expires_at_str.replace("Z", "+00:00")
                        )
                        if datetime.now(timezone.utc) > expires_at:
                            logger.info(f"Session expired: {session.get('id')}")
                            await self.invalidate_session(session_token)
                            return None
                    except Exception:
                        pass
                user = session.get("astra_users", {})
                return {
                    "session_id":    str(session["id"]),
                    "user_id":       session["user_id"],
                    "user":          {
                        "id":             user.get("id"),
                        "email":          user.get("email"),
                        "name":           user.get("name"),
                        "picture":        user.get("picture"),
                        "email_verified": user.get("email_verified", False),
                    },
                    "created_at":    session.get("created_at"),
                    "last_accessed": session.get("last_accessed"),
                    "expires_at":    session.get("expires_at"),
                }
        except Exception as e:
            logger.warning(f"[FALLBACK] Supabase get_session failed ({e}). Checking memory store.")

        # ── In-memory path ────────────────────────────────────────────────────
        return self._mem_get(session_token)

    async def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session in Supabase and/or memory store."""
        invalidated = False

        # Memory
        if session_token in _mem_sessions:
            _mem_sessions[session_token]["is_active"] = False
            invalidated = True

        # Supabase
        try:
            if not db_manager.client:
                return invalidated
            res = (
                db_manager.client
                .table("astra_sessions")
                .update({"is_active": False})
                .eq("session_token", session_token)
                .execute()
            )
            if res.data:
                logger.info(f"Invalidated Supabase session {res.data[0]['id']}")
                invalidated = True
        except Exception as e:
            logger.warning(f"Supabase invalidate_session error (non-fatal): {e}")

        return invalidated

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        count = 0
        # Memory cleanup
        expired_keys = [
            k for k, v in _mem_sessions.items()
            if not v.get("is_active")
        ]
        for k in expired_keys:
            del _mem_sessions[k]
            count += 1

        # Supabase cleanup
        try:
            if not db_manager.client:
                return count
            current_time = datetime.now(timezone.utc).isoformat()
            res = (
                db_manager.client
                .table("astra_sessions")
                .update({"is_active": False})
                .lt("expires_at", current_time)
                .eq("is_active", True)
                .execute()
            )
            count += len(res.data) if res.data else 0
        except Exception as e:
            logger.warning(f"Supabase cleanup error (non-fatal): {e}")

        logger.info(f"Cleaned up {count} expired sessions")
        return count


# Global instance
session_manager = SessionManager()