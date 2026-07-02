import logging
import time
import os
from typing import Optional, Dict, List
from collections import defaultdict

from fastapi import Request, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import verify_token
from app.security_utils import detect_prompt_injection, mask_pii

logger = logging.getLogger(__name__)

# Security Scheme
security = HTTPBearer(auto_error=False)

class RateLimiter:
    """
    Advanced sliding window rate limiter with auto-jailing for persistent offenders.
    """
    def __init__(self, requests_per_minute: int = 60, jail_duration_seconds: int = 3600):
        self.requests_per_minute = requests_per_minute
        self.jail_duration_seconds = jail_duration_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.jail_list: Dict[str, float] = {}
        self.violation_count: Dict[str, int] = defaultdict(int)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        
        # Check if in jail
        if client_id in self.jail_list:
            if now < self.jail_list[client_id]: return False
            self.jail_list.pop(client_id, None) # Released
            self.violation_count[client_id] = 0

        minute_ago = now - 60
        self.requests[client_id] = [t for t in self.requests[client_id] if t > minute_ago]

        if len(self.requests[client_id]) >= self.requests_per_minute:
            self.violation_count[client_id] += 1
            if self.violation_count[client_id] >= 5: # 5 strikes = Jail
                self.jail_list[client_id] = now + self.jail_duration_seconds
                logger.error(f"🚨 SECURITY EVENT: IP {client_id} has been JAILED for {self.jail_duration_seconds}s.")
            return False

        self.requests[client_id].append(now)
        return True

# Initialize global rate limiter with auto-jail
rate_limiter = RateLimiter(requests_per_minute=60, jail_duration_seconds=3600)

async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> bool:
    """
    Mandatory API Key check for server-to-server or high-privilege calls.
    Protects the AI Engine from unauthorized scraping and DoS.
    """
    expected_key = os.getenv("ASTRA_API_KEY", "astra-secret-2026")
    if not x_api_key or x_api_key != expected_key:
        preview = (str(x_api_key)[:5] + "***") if x_api_key else "NONE"
        logger.warning(f"Unauthorized API Key attempt: {preview}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing ASTRA-API-KEY"
        )
    return True

async def content_safety_check(
    request: Request
) -> None:
    """
    Mandatory check of the request body for prompt injection and DoS.
    """
    try:
        # PEEK into the body without consuming it
        body = await request.body()
        if not body: return
        
        text = body.decode('utf-8')
        # Masking logs
        masked_text = mask_pii(text[:100])
        logger.info(f"Incoming Request Content Trace: {masked_text}...")
        
        # Injection detection
        if detect_prompt_injection(text):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Violation: Malicious prompt attempt denied."
            )
    except HTTPException:

        raise

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Safety check error: {e}")
        # Default fail-safe: Allow if unable to parse (e.g. non-JSON)
        return

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Dependency to get the UID if authenticated.
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload.get("uid")
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

async def rate_limit_check(request: Request) -> None:
    """
    Dependency to enforce rate limits based on Client IP.
    """
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

async def validate_user_access(
    user_id_from_request: str,
    authenticated_user: Optional[str] = None
) -> None:
    """
    Logic to ensure a user is only accessing their own resources.
    """
    if authenticated_user is None:
        return

    if user_id_from_request != authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot access another user's data."
        )
