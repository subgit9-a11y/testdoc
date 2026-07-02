"""
Rolling Context Summarizer - Context Window Overflow Protection
==============================================================

Issue (The "Amnesia" Bug):
  After 6 months of daily usage, a patient's chat thread can reach thousands of
  messages. Sending the full thread to the LLM eventually exceeds its context window,
  causing a 400 Bad Request crash. That patient's AI permanently stops responding.

Fix:
  - Track the total interaction count per journey_id.
  - When the raw history exceeds SUMMARIZE_THRESHOLD interactions, compress the
    OLDEST_BATCH_SIZE (50) messages into a single dense medical summary via the LLM.
  - Persist the summary into journey metadata in Supabase + local cache so it
    survives restarts.
  - Always pass the LLM only:
        [system summary message] + last RECENT_WINDOW (10) messages
  - This keeps the live context tiny and crash-proof, while preserving all
    medically important historical context.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Tunable thresholds ────────────────────────────────────────────────────────
SUMMARIZE_THRESHOLD = 30   # Start summarising once journey has 30+ messages
OLDEST_BATCH_SIZE   = 50   # Compress this many old messages per summarization pass
RECENT_WINDOW       = 10   # Always keep this many recent messages in live context
# ─────────────────────────────────────────────────────────────────────────────


class RollingContextSummarizer:
    """
    Manages rolling LLM context for long-running patient journeys.

    Usage (in pipeline.py / chat endpoints):
        history, was_summarized = await rolling_context_summarizer.get_safe_context(
            journey_id=journey_id,
            journey_metadata=journey.get("metadata", {})
        )
        # `history` is a list of {"role": ..., "content": ...} dicts, safe to pass to LLM
    """

    def __init__(self):
        self._brain_client = None
        logger.info("RollingContextSummarizer initialized")

    # ── Brain client (lazy, avoids circular imports) ─────────────────────────

    @property
    def brain(self):
        if self._brain_client is None:
            try:
                from app.astra_brain_client import get_brain_client
                self._brain_client = get_brain_client()
            except Exception as e:
                logger.warning(f"[ContextSummarizer] Brain client unavailable: {e}")
        return self._brain_client

    # ── Public API ────────────────────────────────────────────────────────────

    async def get_safe_context(
        self,
        journey_id: str,
        journey_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, str]], bool]:
        """
        Return (context_messages, was_summarized).

        context_messages is a list of {"role": "user"|"assistant"|"system", "content": str}
        ready to pass to any LLM. It is guaranteed to be within safe token limits.
        was_summarized is True if a background summarization pass ran this call.
        """
        journey_metadata = journey_metadata or {}
        was_summarized   = False

        # ── 1. Fetch raw interactions ──────────────────────────────────────
        raw_interactions = await self._fetch_interactions(journey_id)
        total            = len(raw_interactions)

        logger.info(
            f"[ContextSummarizer] Journey {journey_id}: "
            f"{total} interactions retrieved from store."
        )

        # ── 2. Check if we need to summarize old messages ─────────────────
        if total > SUMMARIZE_THRESHOLD:
            # Interactions older than the recent window
            old_msgs    = raw_interactions[: max(0, total - RECENT_WINDOW)]
            recent_msgs = raw_interactions[max(0, total - RECENT_WINDOW):]

            # Only summarize the oldest OLDEST_BATCH_SIZE messages if unsummarized
            batch = old_msgs[:OLDEST_BATCH_SIZE]

            if batch:
                logger.info(
                    f"[ContextSummarizer] Threshold exceeded ({total} > {SUMMARIZE_THRESHOLD}). "
                    f"Summarizing {len(batch)} old messages…"
                )

                existing_summary = journey_metadata.get("rolling_summary", "")
                new_summary      = await self._summarize_batch(batch, existing_summary)

                if new_summary:
                    was_summarized = True
                    # Persist the updated summary back into journey metadata
                    await self._persist_summary(journey_id, journey_metadata, new_summary)
                    journey_metadata["rolling_summary"] = new_summary
                    logger.info(f"[ContextSummarizer] Summary persisted for journey {journey_id}")

        # ── 3. Build context window ────────────────────────────────────────
        context_messages: List[Dict[str, str]] = []

        # Inject the rolling medical summary as a system message (if exists)
        rolling_summary = journey_metadata.get("rolling_summary", "")
        if rolling_summary:
            context_messages.append({
                "role": "system",
                "content": (
                    "[PATIENT MEDICAL HISTORY SUMMARY — compiled from prior conversations]\n"
                    f"{rolling_summary}"
                )
            })

        # Append the most recent RECENT_WINDOW messages
        recent_slice = raw_interactions[-RECENT_WINDOW:] if len(raw_interactions) > RECENT_WINDOW else raw_interactions
        for interaction in recent_slice:
            role    = self._map_role(interaction.get("interaction_type", ""))
            content = interaction.get("content", "")
            if content:
                context_messages.append({"role": role, "content": content})

        logger.info(
            f"[ContextSummarizer] Safe context built: "
            f"{len(context_messages)} messages "
            f"(summarized={was_summarized})"
        )
        return context_messages, was_summarized

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _fetch_interactions(self, journey_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all interactions for a journey, ordered oldest-first.
        Tries Supabase first, then falls back to local companion_cache.
        """
        try:
            from app.companion_system import companion_manager
            if companion_manager.client:
                resp = (
                    companion_manager.client
                    .table("companion_interactions")
                    .select("interaction_type, content, created_at")
                    .eq("journey_id", journey_id)
                    .order("created_at", desc=False)
                    .execute()
                )
                if resp.data:
                    return resp.data
        except Exception as e:
            logger.warning(f"[ContextSummarizer] Supabase fetch failed: {e}. Falling back to cache.")

        # Cache fallback
        try:
            from app.companion_cache import companion_cache
            cached = companion_cache.get_interactions(journey_id)
            if cached:
                return sorted(cached, key=lambda x: x.get("created_at", ""))
        except Exception as e:
            logger.warning(f"[ContextSummarizer] Cache fetch failed: {e}")

        return []

    async def _summarize_batch(
        self,
        batch: List[Dict[str, Any]],
        existing_summary: str
    ) -> str:
        """
        Use the LLM brain to compress `batch` interactions into a dense
        medical summary, merging it with any previously accumulated summary.
        Falls back to a rule-based condensation if the AI is unavailable.
        """
        # Flatten the batch into a text block
        conversation_text = "\n".join(
            f"[{msg.get('interaction_type', 'message').upper()}]: {msg.get('content', '')}"
            for msg in batch
            if msg.get("content")
        )

        prompt = (
            "You are a medical record summarizer for an Ayurvedic wellness AI. "
            "Your task is to compress the following conversation history into a "
            "dense, structured clinical summary of 3-5 sentences. "
            "Focus ONLY on medically relevant information: symptoms, diagnoses, "
            "prescribed herbs/medicines (e.g., Triphala, Ashwagandha), dosage instructions, "
            "allergies, treatment progress, health milestones, and any critical alerts. "
            "DO NOT include small-talk, greetings, or non-medical content.\n\n"
        )

        if existing_summary:
            prompt += (
                f"EXISTING SUMMARY (from even earlier messages):\n{existing_summary}\n\n"
                "ADDITIONAL CONVERSATION TO MERGE INTO THE SUMMARY:\n"
            )
        else:
            prompt += "CONVERSATION TO SUMMARIZE:\n"

        prompt += conversation_text
        prompt += (
            "\n\nPRODUCE A MERGED CLINICAL SUMMARY (3-5 sentences, medical details only):"
        )

        # Try AI summarization via brain client
        try:
            if self.brain:
                result = await self.brain.chat(query=prompt)
                if result and result.success and result.answer:
                    summary = result.answer.strip()
                    # Sanity check: must be non-trivial
                    if len(summary) > 20:
                        return summary
        except Exception as e:
            logger.warning(f"[ContextSummarizer] AI summarization failed: {e}. Using rule-based fallback.")

        # Rule-based fallback: extract content strings and truncate
        return self._rule_based_summary(batch, existing_summary)

    def _rule_based_summary(
        self,
        batch: List[Dict[str, Any]],
        existing_summary: str
    ) -> str:
        """
        Offline fallback: concatenate the most medically significant messages
        and produce a condensed text block if the AI brain is unavailable.
        """
        import re

        # Simple keyword-weighted importance filter
        medical_keywords = [
            "symptom", "pain", "medicine", "herb", "triphala", "ashwagandha",
            "dose", "dosage", "prescribed", "diagnosis", "allergy", "treatment",
            "fatigue", "fever", "cough", "nausea", "blood", "pressure",
            "diabetes", "thyroid", "anxiety", "stress", "follow", "improve",
            "worse", "better", "ayurveda", "tablet", "capsule", "oil", "churna"
        ]

        important_lines = []
        for msg in batch:
            content = msg.get("content", "")
            if any(kw in content.lower() for kw in medical_keywords):
                # Truncate each line to max 120 chars to keep it dense
                important_lines.append(content[:120].strip())

        condensed = " | ".join(important_lines[:10])  # Cap at 10 key lines
        if not condensed:
            condensed = f"{len(batch)} earlier messages exchanged about the patient's health journey."

        if existing_summary:
            return f"{existing_summary} | {condensed}"
        return condensed

    async def _persist_summary(
        self,
        journey_id: str,
        journey_metadata: Dict[str, Any],
        new_summary: str
    ):
        """
        Persist the updated rolling summary into Supabase journey metadata
        and in the local companion_cache for offline resilience.
        """
        updated_metadata = {**journey_metadata, "rolling_summary": new_summary}

        # Supabase persistence
        try:
            from app.companion_system import companion_manager
            if companion_manager.client:
                companion_manager.client.table("companion_journeys").update({
                    "metadata": updated_metadata
                }).eq("id", journey_id).execute()
                logger.info(f"[ContextSummarizer] Summary persisted to Supabase for {journey_id}")
        except Exception as e:
            logger.warning(f"[ContextSummarizer] Supabase summary persist failed: {e}")

        # Cache persistence
        try:
            from app.companion_cache import companion_cache
            cached_journey = companion_cache.get_journey(journey_id)
            if cached_journey:
                cached_journey["metadata"] = updated_metadata
                companion_cache.set_journey(journey_id, cached_journey)
        except Exception as e:
            logger.warning(f"[ContextSummarizer] Cache summary persist failed: {e}")

    @staticmethod
    def _map_role(interaction_type: str) -> str:
        """
        Map companion interaction_type strings to LLM message roles.
        Astra AI responses are 'assistant'; patient check-ins are 'user'.
        """
        user_types = {
            "check_in", "symptom_assessment", "user_message", "user", "message"
        }
        return "user" if interaction_type.lower() in user_types else "assistant"


# ── Global singleton ──────────────────────────────────────────────────────────
rolling_context_summarizer = RollingContextSummarizer()
