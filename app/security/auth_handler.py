from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    TEMPORARY AUTH HANDLER

    - Accepts Bearer token
    - Does NOT validate yet
    - Allows backend to boot
    - Replace later with Firebase verification
    """

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    return {
        "uid": "temporary-user",
        "role": "user",
        "token": credentials.credentials
    }

