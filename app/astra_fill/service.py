from app.database import db_manager
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.astra_fill.models import (
    AstraFillExtraction, 
    HealthIntakeSchema, 
    ConfidenceLevel,
    AstraFillConfirmationRequest,
    VoiceTranscriptPending,
    VoiceTranscriptConfirmation,
    VoiceChatTranscriptPending,
    VoiceChatConfirmation,
)
from app.astra_fill.extraction import HealthExtractor
from app.model_service import model_service
from app.astra.voice_service import VoiceService
from app.indictrans2_service import indictrans2_service
from app.language_utils import language_manager

logger = logging.getLogger(__name__)

class AstraFillService:
    def __init__(self):
        self.extractor = HealthExtractor(model_service)
        self.voice_service = VoiceService(stt_provider="whisper")

    async def process_voice_intake(self, audio_data: bytes, user_id: str, language_code: str = "en-IN") -> Any:
        asr_result = await self.voice_service.speech_to_text(audio_data, language_code=language_code)
        transcript = asr_result.get("transcript", "")
        
        if not transcript:
            raise ValueError("No speech detected in audio")

        return await self.process_text_intake(transcript, user_id, source="voice")

    async def process_text_intake(self, text: str, user_id: str, source: str = "text") -> Any:
        """
        Full pipeline for text intake: Detect -> Normalize -> Extract -> Save to Supabase
        """
        # 2. Language Detection & Normalization
        detection_result = language_manager.enhanced_language_detection(text)
        detected_lang = detection_result.get("language", "en")
        
        normalized_text = text
        if detected_lang != "en":
            # Translate to English for extraction
            translation_result = await indictrans2_service.translate(text, detected_lang, "en")
            if translation_result.get("success"):
                normalized_text = translation_result.get("translation")
            else:
                logger.warning(f"Normalization failed for language {detected_lang}, using original text")

        # 3. Information Extraction
        extraction_result = await self.extractor.extract_health_details(normalized_text, language="en")
        
        # 4. Create Extraction Object
        extraction_id = str(uuid.uuid4())
        astra_extraction = AstraFillExtraction(
            structured_data=HealthIntakeSchema(**extraction_result["structured_data"]),
            confidences=extraction_result["confidences"],
            raw_transcript=text,
            normalized_text=normalized_text,
            language=detected_lang,
            source=f"astra_fill_{source}",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store in Supabase for persistence
        if db_manager.is_connected():
            await db_manager.save_astra_fill_extraction(
                extraction_id, 
                user_id, 
                astra_extraction.model_dump() if hasattr(astra_extraction, "model_dump") else astra_extraction.dict()
            )
        else:
            logger.warning("Supabase not connected, extraction will not be persistent across restarts")
        
        return astra_extraction, extraction_id

    async def confirm_extraction(self, request: AstraFillConfirmationRequest) -> bool:
        """
        Handles the user confirmation gate.
        Merges confirmed data into the system/RAG/Supabase.
        """
        if not request.user_confirmed:
            logger.info(f"Extraction {request.extraction_id} rejected by user")
            if db_manager.is_connected():
                await db_manager.update_astra_fill_status(request.extraction_id, "rejected")
            return False

        # Retrieve from Supabase
        extraction_record = None
        if db_manager.is_connected():
            extraction_record = await db_manager.get_astra_fill_extraction(request.extraction_id)
        
        if not extraction_record:
            logger.error(f"Extraction ID {request.extraction_id} not found in database")
            return False

        # Use confirmed data from request (user might have edited)
        final_data = request.confirmed_data

        # 5. Merge with RAG / Database 
        # For now, we update the status in astra_fill_extractions and log
        if db_manager.is_connected():
            await db_manager.update_astra_fill_status(request.extraction_id, "confirmed")
            
            # Optionally update patient profile or clinical notes
            # This could be a future enhancement to sync with EHR
            logger.info(f"✅ Confirmed health intake for user {extraction_record['user_id']}: {final_data.dict()}")
        
        return True
        
    async def get_latest_fill(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest confirmed/pending health intake for a patient"""
        if not db_manager.is_connected():
            return None
        return await db_manager.get_latest_astra_fill(user_id)

    async def get_fill_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve full health intake history for a patient"""
        if not db_manager.is_connected():
            return []
        return await db_manager.get_astra_fill_history(user_id)

    async def process_voice_chat(self, audio_data: bytes, user_id: str, language_code: str = "en-IN") -> Dict[str, Any]:
        """
        Relay voice audio to STT then to the Astra AI Brain for a response.
        NOTE: This method is retained for backward compatibility only.
        New flows MUST use transcribe_voice_for_chat_confirmation() + confirm_and_chat_voice().
        """
        from app.astra_brain_client import astra_brain
        
        # 1. Audio to Text
        asr_result = await self.voice_service.speech_to_text(audio_data, language_code=language_code)
        transcript = asr_result.get("transcript", "")
        
        if not transcript:
            return {"success": False, "error": "No speech detected"}

        # 2. Text to AI Brain
        brain_response = await astra_brain.chat(transcript)
        
        # 3. SAVE to Supabase for persistence
        if db_manager.is_connected():
            await db_manager.save_chat_message(
                user_id=user_id,
                user_message=transcript,
                assistant_response=brain_response.answer,
                language=language_code,
                metadata={"source": "astra_voice_assistant", "voice": True}
            )
            logger.info(f"Persisted voice conversation for user {user_id}")

        return {
            "success": True,
            "transcript": transcript,
            "response": brain_response.answer,
            "mode": brain_response.mode
        }

    # ========================================================================
    # TWO-PHASE VOICE CONFIRMATION GATE
    # Phase 1: STT only  -> return transcript to UI for human review
    # Phase 2: AI runs   -> only after patient confirms the transcript
    # ========================================================================

    # Pending transcript in-memory store (TTL-backed).
    # Keyed by pending_id -> {"transcript": str, "user_id": str, "expires_at": datetime, "language_code": str}
    _pending_transcripts: Dict[str, Dict[str, Any]] = {}

    # TTL for unconfirmed transcripts (10 minutes)
    _PENDING_TTL_MINUTES = 10

    def _build_ui_prompt(self, transcript: str, confidence: Optional[float]) -> str:
        """Build the ready-to-display confirmation prompt for the Flutter UI card."""
        low_confidence_warning = ""
        if confidence is not None and confidence < 0.75:
            low_confidence_warning = (
                " ⚠️ Low audio quality detected — please review carefully."
            )
        return (
            f'I heard: "{transcript}". '
            f"Is this correct?{low_confidence_warning}"
        )

    async def transcribe_voice_for_confirmation(
        self,
        audio_data: bytes,
        user_id: str,
        language_code: str = "en-IN"
    ) -> VoiceTranscriptPending:
        """
        PHASE 1 — Voice Intake Safety Gate
        
        Runs Speech-to-Text ONLY.
        Does NOT trigger any AI extraction or medical workflow.
        Returns a VoiceTranscriptPending that the Flutter UI must present
        as a confirmation card: 'I heard: "...". Is this correct? [Yes / Edit]'
        
        The AI extraction only runs when confirm_and_process_voice() is called
        with user_confirmed=True.
        """
        # 1. STT — this is the ONLY operation in Phase 1
        asr_result = await self.voice_service.speech_to_text(audio_data, language_code=language_code)
        transcript  = asr_result.get("transcript", "").strip()
        confidence  = asr_result.get("confidence")  # float or None

        if not transcript:
            raise ValueError("No speech detected in audio. Please try speaking more clearly.")

        # 2. Generate a short-lived pending ID
        pending_id  = str(uuid.uuid4())
        now         = datetime.utcnow()
        expires_at  = now + timedelta(minutes=self._PENDING_TTL_MINUTES)

        # 3. Store pending transcript in memory (+ optionally Supabase)
        self._pending_transcripts[pending_id] = {
            "transcript":   transcript,
            "user_id":      user_id,
            "language_code": language_code,
            "confidence":   confidence,
            "expires_at":   expires_at,
        }
        self._purge_expired_pending()  # housekeeping

        # Optionally persist to Supabase for cross-process durability
        if db_manager.is_connected():
            try:
                await db_manager.save_pending_voice_transcript(
                    pending_id=pending_id,
                    user_id=user_id,
                    transcript=transcript,
                    language_code=language_code,
                    confidence=confidence,
                    expires_at=expires_at.isoformat()
                )
            except Exception as e:
                logger.warning(f"[VoiceGate] Could not persist pending transcript to Supabase: {e}")

        logger.info(
            f"[VoiceGate] Phase 1 complete for user {user_id}. "
            f"pending_id={pending_id}, confidence={confidence}"
        )

        return VoiceTranscriptPending(
            pending_id=pending_id,
            user_id=user_id,
            raw_transcript=transcript,
            language_code=language_code,
            confidence_score=confidence,
            requires_confirmation=True,
            ui_prompt=self._build_ui_prompt(transcript, confidence),
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat()
        )

    async def confirm_and_process_voice(
        self,
        confirmation: VoiceTranscriptConfirmation
    ) -> Dict[str, Any]:
        """
        PHASE 2 — Voice Intake: Process confirmed transcript
        
        Only runs after the patient has explicitly approved the transcript.
        Validates the pending_id, checks TTL, then triggers AI extraction
        on the human-verified text.
        """
        # 1. Validate user intent
        if not confirmation.user_confirmed:
            logger.info(f"[VoiceGate] User rejected transcript for pending_id={confirmation.pending_id}")
            self._pending_transcripts.pop(confirmation.pending_id, None)
            return {"status": "rejected", "message": "Transcript rejected by user. No medical data was processed."}

        # 2. Retrieve and validate the pending record
        pending = self._resolve_pending(confirmation.pending_id, confirmation.user_id)
        if pending is None:
            raise ValueError(
                "Voice transcript confirmation expired or not found. "
                f"Please re-record your message (timeout: {self._PENDING_TTL_MINUTES} minutes)."
            )

        # 3. Use the patient's verified transcript (may differ from raw if edited)
        verified_text = confirmation.confirmed_transcript.strip()
        if not verified_text:
            raise ValueError("Confirmed transcript cannot be empty.")

        logger.info(
            f"[VoiceGate] Phase 2 confirmed for user {confirmation.user_id}. "
            f"Verified text: '{verified_text[:80]}...'"
        )

        # 4. NOW trigger the full AI extraction pipeline on the verified text
        extraction, extraction_id = await self.process_text_intake(
            text=verified_text,
            user_id=confirmation.user_id,
            source="voice_confirmed"
        )

        # 5. Clean up the pending entry
        self._pending_transcripts.pop(confirmation.pending_id, None)

        return {
            "status": "success",
            "extraction_id": extraction_id,
            "confirmed_transcript": verified_text,
            "data": extraction.model_dump() if hasattr(extraction, "model_dump") else extraction.dict()
        }

    async def transcribe_voice_for_chat_confirmation(
        self,
        audio_data: bytes,
        user_id: str,
        language_code: str = "en-IN"
    ) -> VoiceChatTranscriptPending:
        """
        PHASE 1 — Voice Chat Safety Gate
        
        Runs STT only for the voice assistant chat flow.
        Returns the raw transcript for UI confirmation before sending to AI Brain.
        """
        asr_result = await self.voice_service.speech_to_text(audio_data, language_code=language_code)
        transcript  = asr_result.get("transcript", "").strip()
        confidence  = asr_result.get("confidence")

        if not transcript:
            raise ValueError("No speech detected in audio.")

        pending_id = str(uuid.uuid4())
        now        = datetime.utcnow()
        expires_at = now + timedelta(minutes=self._PENDING_TTL_MINUTES)

        self._pending_transcripts[pending_id] = {
            "transcript":   transcript,
            "user_id":      user_id,
            "language_code": language_code,
            "confidence":   confidence,
            "expires_at":   expires_at,
            "type":         "chat",
        }
        self._purge_expired_pending()

        return VoiceChatTranscriptPending(
            pending_id=pending_id,
            user_id=user_id,
            raw_transcript=transcript,
            language_code=language_code,
            confidence_score=confidence,
            requires_confirmation=True,
            ui_prompt=self._build_ui_prompt(transcript, confidence),
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat()
        )

    async def confirm_and_chat_voice(
        self,
        confirmation: VoiceChatConfirmation
    ) -> Dict[str, Any]:
        """
        PHASE 2 — Voice Chat: Send confirmed transcript to AI Brain.
        """
        if not confirmation.user_confirmed:
            self._pending_transcripts.pop(confirmation.pending_id, None)
            return {"success": False, "message": "Voice input rejected by user."}

        pending = self._resolve_pending(confirmation.pending_id, confirmation.user_id)
        if pending is None:
            raise ValueError(
                f"Voice chat confirmation expired. Please re-record (timeout: {self._PENDING_TTL_MINUTES} minutes)."
            )

        verified_text = confirmation.confirmed_transcript.strip()
        if not verified_text:
            raise ValueError("Confirmed transcript cannot be empty.")

        logger.info(f"[VoiceGate] Chat Phase 2 confirmed: '{verified_text[:80]}...'")

        from app.astra_brain_client import astra_brain
        brain_response = await astra_brain.chat(verified_text)

        if db_manager.is_connected():
            await db_manager.save_chat_message(
                user_id=confirmation.user_id,
                user_message=verified_text,
                assistant_response=brain_response.answer,
                language=confirmation.language_code or "en-IN",
                metadata={"source": "astra_voice_confirmed", "voice": True, "confirmed": True}
            )

        self._pending_transcripts.pop(confirmation.pending_id, None)

        return {
            "success": True,
            "confirmed_transcript": verified_text,
            "response": brain_response.answer,
            "mode": brain_response.mode
        }

    def _resolve_pending(
        self,
        pending_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Look up a pending transcript, validate ownership and TTL.
        Returns None if expired, missing, or owned by a different user.
        """
        self._purge_expired_pending()
        record = self._pending_transcripts.get(pending_id)
        if not record:
            return None
        if record["user_id"] != user_id:
            logger.warning(
                f"[VoiceGate] pending_id {pending_id} user mismatch: "
                f"expected {record['user_id']}, got {user_id}"
            )
            return None
        return record

    def _purge_expired_pending(self):
        """Remove expired pending transcripts to prevent memory growth."""
        now = datetime.utcnow()
        expired = [
            pid for pid, rec in self._pending_transcripts.items()
            if rec["expires_at"] < now
        ]
        for pid in expired:
            del self._pending_transcripts[pid]
        if expired:
            logger.debug(f"[VoiceGate] Purged {len(expired)} expired pending transcripts")


# Global singleton
astra_fill_service = AstraFillService()
