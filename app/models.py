
"""
Pydantic models for API requests and responses
"""

from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# =====================================================
# CHAT MODES (CRITICAL FIX)
# =====================================================
ChatMode = Literal[
    "wellness",        # Default Astra wellness companion
    "clinical",        # Doctor-style Ayurvedic explanation
    "student",         # BAMS / learning mode
    "prescription"     # Dosage / prescription explanation
]

# =====================================================
# BASIC CHAT
# =====================================================

class ChatRequest(BaseModel):
    """Request model for chat completion"""
    message: str = Field(..., description="The input message/prompt")

    mode: Optional[ChatMode] = Field(
        "wellness",
        description="Response mode: wellness | clinical | student | prescription"
    )

    language: Optional[str] = Field(None, description="Preferred language")

    max_length: Optional[int] = Field(1024, description="Maximum length of generated text")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    top_p: Optional[float] = Field(0.9, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(50, description="Top-k sampling parameter")
    do_sample: Optional[bool] = Field(True, description="Whether to use sampling")


class ChatResponse(BaseModel):
    """Response model for chat completion"""
    response: str
    model: str
    usage: Optional[Dict[str, int]] = None


# =====================================================
# HEALTH & MODEL STATUS
# =====================================================

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    device: str


class ModelStatus(BaseModel):
    loaded: bool
    base_model: str
    lora_model: str
    device: str
    memory_usage: Optional[Dict[str, Any]] = None


# =====================================================
# SESSION MODELS
# =====================================================

class ChatSessionRequest(BaseModel):
    user_id: str
    language: Optional[str] = "en"


class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: str
    language: str
    created_at: datetime


# =====================================================
# ENHANCED CHAT (MOST IMPORTANT)
# =====================================================

class EnhancedChatRequest(BaseModel):
    message: str

    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: Optional[str] = None

    mode: Optional[ChatMode] = Field(
        "wellness",
        description="Controls Astra response behavior"
    )

    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True


class EnhancedChatResponse(BaseModel):
    response: str
    session_id: Optional[str]
    language: str
    is_ayurveda_related: bool
    model: str
    usage: Optional[Dict[str, int]] = None


# =====================================================
# CHAT HISTORY
# =====================================================

class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    session_info: Dict[str, Any]


class UserSessionsResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    total_count: int


# =====================================================
# AUTHENTICATION MODELS
# =====================================================

class AuthRequest(BaseModel):
    access_token: str


class SessionResponse(BaseModel):
    session_token: str
    session_id: str
    user: Dict[str, Any]
    expires_at: str


class UserInfo(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False


class AuthenticatedChatRequest(BaseModel):
    message: str
    session_token: Optional[str] = None
    language: Optional[str] = None

    mode: Optional[ChatMode] = "wellness"

    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True


class AuthenticatedChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    language: str
    is_ayurveda_related: bool
    model: str
    usage: Optional[Dict[str, int]] = None
    created_at: str


# =====================================================
# STREAMING CHAT
# =====================================================

class StreamingChatRequest(BaseModel):
    message: str
    language: Optional[str] = None

    mode: Optional[ChatMode] = "wellness"

    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    user_id: Optional[str] = None
    session_id: Optional[str] = None


# =====================================================
# CHAT HISTORY REQUEST
# =====================================================

class ChatHistoryRequest(BaseModel):
    session_token: str
    session_id: Optional[str] = None
    limit: Optional[int] = 50

