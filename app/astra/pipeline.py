"""
Astra Pipeline - Central AI Processing Hub
Now connected to ALL Astra Companion endpoints via AstraBrainClient
"""

import logging
import json
from typing import Optional, List, Dict, Any

# Rolling Context Summarizer — prevents context-window overflow (Amnesia Bug fix)
from app.rolling_context_summarizer import rolling_context_summarizer

logger = logging.getLogger(__name__)


class AstraPipeline:
    """
    Central pipeline that orchestrates all AI-powered features
    Connected to Astra Companion for intelligence
    """
    
    def __init__(self, inference=None, capability_agent=None):
        self.inference = inference
        self.capability_agent = capability_agent
        self._brain_client = None
        logger.info("✅ AstraPipeline initialized")
    
    @property
    def brain(self):
        """Lazy load the brain client"""
        if self._brain_client is None:
            from app.astra_brain_client import get_brain_client
            self._brain_client = get_brain_client()
        return self._brain_client

    async def process_query(
        self,
        user_id: str,
        message: str,
        history: list,
        journey_id: Optional[str] = None,
        journey_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main query processing with full AI pipeline:
        1. Rolling context summarization (Amnesia Bug prevention)
        2. Safety check
        3. Emotion detection
        4. AI response generation with safe context
        5. Capability action processing
        """
        try:
            # 1. Build safe rolling context (prevents context-window overflow)
            context_messages: List[Dict[str, str]] = []
            was_summarized = False
            effective_journey_id = journey_id or user_id

            try:
                context_messages, was_summarized = await rolling_context_summarizer.get_safe_context(
                    journey_id=effective_journey_id,
                    journey_metadata=journey_metadata or {}
                )
                if was_summarized:
                    logger.info(
                        f"[PIPELINE] Rolling summary triggered for journey {effective_journey_id}. "
                        f"Context window is now crash-proof."
                    )
            except Exception as ctx_err:
                logger.warning(f"[PIPELINE] Context summarizer skipped: {ctx_err}")
                # Graceful degradation: use raw history tail if summarizer fails
                context_messages = [
                    {"role": "user" if i % 2 == 0 else "assistant", "content": str(h)}
                    for i, h in enumerate(history[-10:])
                ]

            # Build a compact context string to inject into the brain query
            context_str = ""
            if context_messages:
                context_str = "\n".join(
                    f"{m['role'].upper()}: {m['content']}"
                    for m in context_messages
                )

            # 2. Safety Analysis
            safety_result = await self.brain.analyze_safety(message)
            if not safety_result.is_safe:
                logger.warning(f"[SAFETY] Flags detected: {safety_result.flags}")
                if "self_harm" in safety_result.flags:
                    return self._get_crisis_response()
                if "emergency" in safety_result.flags:
                    return "[ESCALATE] This appears to be an emergency. Please contact emergency services or visit the nearest hospital."

            # 3. Emotion Detection
            try:
                emotion = await self.brain.detect_emotion(message)
                emot_str = str(emotion.emotion)[:50]
                logger.info(f"[EMOTION] User state: {emot_str} ({emotion.intensity})")
            except Exception as e:
                logger.warning(f"[PIPELINE] Emotion detection skipped: {e}")

            # 4. Get AI Response, injecting the safe rolling context
            query_with_context = (
                f"{context_str}\nUSER: {message}"
                if context_str else message
            )
            chat_result = await self.brain.chat(query=query_with_context)

            if chat_result.success:
                raw_response = chat_result.answer
            else:
                # Fallback to legacy inference if brain fails
                if self.inference:
                    system_instruction = (
                        "SYSTEM: To take action, output JSON inside [ACTION:...] tag. "
                        "To escalate to human, output [ESCALATE]."
                    )
                    full_prompt = (
                        f"{system_instruction}\n"
                        f"Context:\n{context_str}\n"
                        f"User: {message}"
                    )
                    raw_response = await self.inference.generate_response(full_prompt)
                else:
                    raw_response = "I apologize, but I'm having trouble connecting. Please try again."

            # 5. Process Actions (Automation/Escalation)
            final_response = raw_response
            if self.capability_agent:
                result = self.capability_agent.process_response_actions(raw_response)
                final_response = result.get("modified_response", raw_response)

            # --- PERSISTENCE ---
            try:
                from app.database import db_manager
                if db_manager.is_connected():
                    await db_manager.save_chat_message(
                        user_id=user_id,
                        user_message=message,
                        assistant_response=final_response,
                        metadata={
                            "source": "astra_pipeline_central",
                            "pipelined": True,
                            "context_summarized": was_summarized
                        }
                    )
                    logger.info(f"[STORAGE] Conversation archived for user {user_id}")
            except Exception as e:
                logger.error(f"[STORAGE] Failed to persist pipeline conversation: {e}")

            return final_response

        except Exception as e:
            logger.error(f"[PIPELINE] Error: {e}")
            return "I encountered an issue processing your request. Please try again."

    async def process_query_stream(
        self,
        user_id: str,
        message: str,
        history: list,
        journey_id: Optional[str] = None,
        journey_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Streaming version of process_query.
        Yields chunks from the brain client.
        """
        try:
            # 1. Build safe rolling context (prevents context-window overflow)
            context_messages: List[Dict[str, str]] = []
            was_summarized = False
            effective_journey_id = journey_id or user_id

            try:
                context_messages, was_summarized = await rolling_context_summarizer.get_safe_context(
                    journey_id=effective_journey_id,
                    journey_metadata=journey_metadata or {}
                )
            except Exception as ctx_err:
                logger.warning(f"[PIPELINE] Context summarizer skipped: {ctx_err}")
                context_messages = [
                    {"role": "user" if i % 2 == 0 else "assistant", "content": str(h)}
                    for i, h in enumerate(history[-10:])
                ]

            context_str = ""
            if context_messages:
                context_str = "\n".join(
                    f"{m['role'].upper()}: {m['content']}"
                    for m in context_messages
                )

            # 2. Safety Analysis (Synchronous before stream)
            safety_result = await self.brain.analyze_safety(message)
            if not safety_result.is_safe:
                logger.warning(f"[SAFETY] Flags detected: {safety_result.flags}")
                if "self_harm" in safety_result.flags:
                    yield f"data: {json.dumps({'content': self._get_crisis_response()})}\n\n"
                    return
                if "emergency" in safety_result.flags:
                    yield f"data: {json.dumps({'content': '[ESCALATE] This appears to be an emergency. Please contact emergency services.'})}\n\n"
                    return

            # 3. Stream Response
            query_with_context = (
                f"{context_str}\nUSER: {message}"
                if context_str else message
            )
            
            full_response = ""
            async for chunk in self.brain.chat_stream(query=query_with_context):
                yield chunk
                # In a real app we'd parse the SSE here to build full_response if we wanted to save to DB
                # But since it's a proxy, the GPU server already saves to its own DB!

        except Exception as e:
            logger.error(f"[PIPELINE STREAM] Error: {e}")
            import json
            yield f"data: {json.dumps({'error': 'I encountered an issue processing your request.'})}\n\n"

    
    async def route_intent(self, query: str) -> Dict[str, Any]:
        """
        Use autopilot to determine user intent
        Returns: {"intent": "CHAT|SHOP_ASSIST|BOOKING", "action": ...}
        """
        result = await self.brain.autopilot(query)
        return {
            "intent": result.intent.value,
            "status": result.status,
            "should_route": result.intent.value != "CHAT"
        }
    
    async def extract_data(self, text: str, schema: str) -> Dict[str, Any]:
        """
        Extract structured data from text using /v1/fill
        """
        return await self.brain.fill(text, schema)
    
    async def get_shop_recommendations(self, query: str) -> Dict[str, Any]:
        """
        Get product recommendations using /v1/shop_assist
        """
        return await self.brain.shop_assist(query)
    
    async def extract_reminders(self, prescription_text: str) -> Dict[str, Any]:
        """
        Extract medication reminders using /v1/extract_schedule
        """
        result = await self.brain.extract_schedule(prescription_text)
        return {
            "reminders": result.reminders,
            "raw": result.raw_json
        }
    
    async def summarize_for_doctor(self, patient_notes: str) -> Dict[str, Any]:
        """
        Generate clinical summary using /v1/doctor_summary
        """
        return await self.brain.doctor_summary(patient_notes)
    
    async def generate_wellness_content(self, topic: str, duration: str = "5 mins") -> Dict[str, Any]:
        """
        Generate meditation/yoga content using /v1/generate_wellness
        """
        return await self.brain.generate_wellness(topic, duration)
    
    async def match_buddy(self, profile_a: str, profile_b: str = None) -> Dict[str, Any]:
        """
        Analyze profiles for buddy matching using /v1/profile_analysis
        """
        return await self.brain.profile_analysis(profile_a, "buddy_match", profile_b)
    
    async def rewrite_empathetic(self, text: str) -> str:
        """
        Rewrite text to be more empathetic using /v1/adjust_tone
        """
        result = await self.brain.adjust_tone(text, "empathetic")
        return result.get("rewritten_text", text)
    
    def _get_crisis_response(self) -> str:
        """Return crisis intervention response"""
        return """I'm concerned about what you've shared. Your wellbeing matters deeply to us.

🆘 **If you're in crisis, please reach out immediately:**
- **India**: iCall: 9152987821 | Vandrevala Foundation: 1860-2662-345
- **Emergency**: Dial 112

You don't have to face this alone. A trained counselor can help right now.

Would you like me to connect you with our care team? [ESCALATE]"""

    # Backward compatibility for Autopilot and other legacy modules
    async def run(
        self,
        input_text: str,
        user_uuid: str = None,
        channel: str = None,
        metadata: dict = None
    ):
        """Legacy interface - maps to process_query, now with rolling context support."""
        journey_id = None
        journey_metadata = None
        if metadata:
            journey_id       = metadata.get("journey_id")
            journey_metadata = metadata.get("journey_metadata")  # caller may inject

        return await self.process_query(
            user_id=user_uuid or "unknown",
            message=input_text,
            history=[],
            journey_id=journey_id,
            journey_metadata=journey_metadata
        )

    async def run_stream(
        self,
        input_text: str,
        user_uuid: str = None,
        channel: str = None,
        metadata: dict = None
    ):
        """Legacy interface - maps to process_query_stream"""
        journey_id = None
        journey_metadata = None
        if metadata:
            journey_id       = metadata.get("journey_id")
            journey_metadata = metadata.get("journey_metadata")

        async for chunk in self.process_query_stream(
            user_id=user_uuid or "unknown",
            message=input_text,
            history=[],
            journey_id=journey_id,
            journey_metadata=journey_metadata
        ):
            yield chunk
