from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class HealthIntakeSchema(BaseModel):
    primary_complaint: str = Field(..., description="The main health issue or reason for intake")
    duration: str = Field(..., description="How long the issue has been present")
    severity_clues: str = Field(..., description="Details about how severe the issue is or what makes it worse")
    pattern_or_timing: str = Field(..., description="When the symptom occurs or its frequency")
    previous_treatment: str = Field(..., description="Any medicines or treatments already tried for this")
    is_follow_up: bool = Field(False, description="Whether this is a follow-up to a previous issue")
    stop_or_gap_sign: Optional[str] = Field(None, description="Signs that treatment was stopped or there was a gap")

class ExtractedField(BaseModel):
    value: Any
    confidence: ConfidenceLevel
    reasoning: Optional[str] = None

class AstraFillExtraction(BaseModel):
    structured_data: HealthIntakeSchema
    confidences: Dict[str, ConfidenceLevel]
    raw_transcript: str
    normalized_text: Optional[str] = None
    language: str
    source: str = "astra_fill"
    timestamp: str

class AstraFillConfirmationRequest(BaseModel):
    session_id: str
    extraction_id: str
    confirmed_data: HealthIntakeSchema
    user_confirmed: bool

# ── Voice Transcript Confirmation Gate (Two-Phase Safety Flow) ────────────────

class VoiceTranscriptPending(BaseModel):
    """
    Phase 1 response: Raw STT result returned to the Flutter UI for human review.
    The AI extraction pipeline is NOT yet triggered.
    The Flutter app MUST display a confirmation card:
      'I heard: "<transcript>". Is this correct? [Yes / Edit]'
    before calling /confirm-transcript.
    """
    pending_id: str = Field(..., description="Short-lived ID for this unconfirmed transcript (TTL: 10 minutes)")
    user_id: str
    raw_transcript: str = Field(..., description="Verbatim STT output — may contain errors")
    language_code: str
    confidence_score: Optional[float] = Field(
        None,
        description="STT engine confidence (0.0-1.0). Low scores shown as warnings in UI."
    )
    requires_confirmation: bool = Field(
        True,
        description="Always True for voice inputs. UI must gate on user acknowledgment."
    )
    ui_prompt: str = Field(
        default="",
        description="Ready-to-display confirmation prompt for the Flutter UI card."
    )
    created_at: str
    expires_at: str = Field(..., description="ISO timestamp after which this pending_id is invalid")


class VoiceTranscriptConfirmation(BaseModel):
    """
    Phase 2 request: User has reviewed and optionally corrected the transcript.
    Only after receiving this does the backend trigger AI extraction.
    """
    pending_id: str = Field(..., description="Must match the pending_id from Phase 1")
    user_id: str
    confirmed_transcript: str = Field(
        ...,
        description="The transcript as corrected and approved by the patient. "
                    "May differ from raw_transcript if the user made edits."
    )
    user_confirmed: bool = Field(
        ...,
        description="Must be True — False means the user rejected the transcript entirely."
    )
    language_code: Optional[str] = "en-IN"


class VoiceChatTranscriptPending(BaseModel):
    """
    Phase 1 response for the voice assistant chat flow.
    Holds the raw STT transcript for UI confirmation before sending to AI Brain.
    """
    pending_id: str
    user_id: str
    raw_transcript: str
    language_code: str
    confidence_score: Optional[float] = None
    requires_confirmation: bool = True
    ui_prompt: str = ""
    created_at: str
    expires_at: str


class VoiceChatConfirmation(BaseModel):
    """
    Phase 2 request for the voice assistant chat flow.
    Sends the user-verified transcript to the AI Brain.
    """
    pending_id: str
    user_id: str
    confirmed_transcript: str
    user_confirmed: bool
    language_code: Optional[str] = "en-IN"
