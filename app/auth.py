import os
import logging
from typing import Optional, Dict, Any

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import firebase_admin
from firebase_admin import credentials, auth

# Configure Logging
logger = logging.getLogger(__name__)

# Constants
FIREBASE_CREDENTIAL_PATH = os.getenv("FIREBASE_CREDENTIAL_PATH", "firebase_service_account.json")

# Initialize Firebase Admin SDK (Singleton Pattern)
if not firebase_admin._apps:
    try:
        if os.path.exists(FIREBASE_CREDENTIAL_PATH):
            cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully.")
        else:
            logger.warning(f"Firebase credential file not found at: {FIREBASE_CREDENTIAL_PATH}")
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")

security = HTTPBearer()

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token and returns the decoded payload.
    Raises HTTPException if invalid.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token expired"
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Firebase token"
        )
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Token verification unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication failed"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI Dependency: Validates Bearer token and returns user info.
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_info = {
        "user_id": payload.get("uid"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "picture": payload.get("picture"),
        "email_verified": payload.get("email_verified", False)
    }

    if not user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid user data in token"
        )

    return user_info

async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Optional Dependency: Returns user info if token is present, else None.
    Does not raise 401.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        payload = verify_token(token)

        return {
            "user_id": payload.get("uid"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
            "email_verified": payload.get("email_verified", False)
        }
    except Exception:
        return None
