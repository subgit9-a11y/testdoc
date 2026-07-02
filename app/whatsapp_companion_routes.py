"""
WhatsApp Integration Routes for AI Companion
"""

from fastapi import APIRouter, Request, Response, Form, HTTPException
from typing import Optional
import logging

from app.whatsapp_companion_service import whatsapp_companion_service
from app.companion_redis_manager import redis_companion_manager
from app.enhanced_input_validator import input_validator
from app.redis_cache import redis_cache
from app.xss_sanitizer import xss_sanitizer
from app.immutable_audit_logger import audit_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp-companion", tags=["WhatsApp Companion"])

@router.post("/webhook")
async def whatsapp_companion_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: str = Form(None),
    WaId: str = Form(None),
    MessageSid: str = Form(None)
):
    """
    Handle incoming WhatsApp messages
    Integrates with AI Companion system
    """
    try:
        logger.info(f"📱 WhatsApp from {From}: {Body[:50]}")
        
        # Extract phone number
        phone_number = From.replace('whatsapp:', '')
        
        # Rate limiting check
        rate_key = f"rate:{phone_number}"
        message_count = redis_cache.get("whatsapp", rate_key) or 0
        
        if message_count >= 20:  # Max 20 messages per hour
            whatsapp_companion_service.send_message(
                From,
                "⚠️ You've reached the message limit. Please try again in an hour."
            )
            return Response(content="", media_type="text/plain")
        
        # Increment rate limit counter (1 hour TTL)
        redis_cache.set("whatsapp", rate_key, message_count + 1, ttl_seconds=3600)
        
        # Validate input
        is_valid, sanitized_msg, error = input_validator.validate_message(Body)
        if not is_valid:
            await whatsapp_companion_service.send_message(
                From,
                f"⚠️ {error}. Please send a valid message."
            )
            return Response(content="", media_type="text/plain")
        
        # Get or create journey
        journey_key = f"journey:{phone_number}"
        journey_id = redis_cache.get("whatsapp", journey_key)
        
        if not journey_id:
            # New user - start journey
            journey_id = await redis_companion_manager.start_companion_journey(
                user_id=phone_number,
                health_concern="general wellness",
                language="en",
                initial_symptoms=[]
            )
            
            if journey_id:
                redis_cache.set("whatsapp", journey_key, journey_id, ttl_seconds=86400 * 30)  # 30 days
                
                # Send welcome
                welcome = f"Hello {ProfileName or 'there'}! 👋\n\nI'm Astra, your AI wellness companion.\n\nI'm here to help with:\n• Health questions\n• Medication reminders\n• Symptom tracking\n• General wellness guidance\n\nHow can I assist you today?"
                
                await whatsapp_companion_service.send_message(From, welcome)
                return Response(content="", media_type="text/plain")
        
        # Get conversation history (last 10 messages)
        history = await redis_companion_manager.get_conversation_history(
            journey_id=journey_id,
            limit=10
        )
        
        # Build conversation context
        from app.conversation_pruner import conversation_pruner
        
        messages = []
        for interaction in history:
            if interaction.get("interaction_type") == "user_message":
                messages.append({
                    "role": "user",
                    "content": interaction.get("content", "")
                })
            elif interaction.get("interaction_type") in ["assistant_response", "whatsapp_response"]:
                messages.append({
                    "role": "assistant",
                    "content": interaction.get("content", "")
                })
        
        # Add current message
        messages.append({"role": "user", "content": sanitized_msg})
        
        # Prune if needed
        messages = conversation_pruner.prune_conversation(messages)
        
        # System prompt optimized for WhatsApp
        system_prompt = """You are Astra, an AI wellness companion on WhatsApp.

Important:
- Keep responses SHORT and CONCISE (max 200 words)
- Use simple language
- Use emojis sparingly (1-2 per message)
- Format with line breaks for readability
- Be warm and friendly
- Provide actionable advice
- Ask clarifying questions if needed
- For emergencies, advise consulting a doctor immediately
- **Cultural Clarification Protocol**: If a patient uses slang, idioms, or metaphors to describe pain (e.g., "My chest is burning", "My head is bursting"), you MUST ask ONE explicit clarifying question (e.g., 'Do you mean indigestion, or is the pain crushing your heart?') before assigning clinical severity or triggering an emergency."""
        
        # Generate AI response with timeout
        import asyncio
        from app.model_service import model_service
        
        try:
            ai_response = await asyncio.wait_for(
                model_service.generate_response(
                    prompt=sanitized_msg,
                    language="en",
                    context=system_prompt
                ),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            ai_response = "I'm taking a bit longer to respond. Please wait a moment and ask again."
            
        # --- XSS SANITIZATION ---
        ai_response = xss_sanitizer.sanitize_text(ai_response)
        
        # --- TOKEN BUDGET MONITOR ACCUMULATION ---
        current_hour = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d-%H')
        budget_key = f"token_usage:{phone_number}:{current_hour}"
        
        estimated_tokens = int((len(sanitized_msg.split()) + len(ai_response.split())) * 1.3)
        
        current_usage = redis_cache.get("budget", budget_key) or 0
        new_usage = current_usage + estimated_tokens
        redis_cache.set("budget", budget_key, new_usage, ttl_seconds=7200)
        
        if new_usage > 2000:
            logger.critical(f"🚨 DENIAL OF WALLET PREVENTED: WhatsApp User {phone_number} exceeded 2000 tokens/hr. Freezing.")
            redis_cache.set("budget", f"frozen:{phone_number}", True, ttl_seconds=86400 * 365)
            
            await whatsapp_companion_service.send_message(
                From,
                "⚠️ **ACCOUNT FROZEN FOR REVIEW** ⚠️\n\nWe detected unusually high activity on your account. Your connection has been severed to prevent abuse. Please contact support."
            )
            return Response(content="", media_type="text/plain")

        # --- IMMUTABLE AUDIT TRAIL LOGGING ---
        audit_logger.log_event(
            event_type="whatsapp_ai_response",
            actor_id=phone_number,
            action_details="AI Companion generated a medical/wellness response via WhatsApp.",
            payload={
                "user_message": sanitized_msg,
                "ai_response": ai_response,
                "tokens_used": estimated_tokens
            },
            session_id=journey_id
        )
        
        # Log interactions
        await redis_companion_manager.log_interaction(
            journey_id=journey_id,
            interaction_type="whatsapp_message",
            content=sanitized_msg,
            language="en"
        )
        
        await redis_companion_manager.log_interaction(
            journey_id=journey_id,
            interaction_type="whatsapp_response",
            content=ai_response,
            language="en"
        )
        
        # Send response
        await whatsapp_companion_service.send_message(From, ai_response)
        
        # Return empty response (Twilio expects this)
        return Response(content="", media_type="text/plain")
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        
        # Send user-friendly error
        try:
            await whatsapp_companion_service.send_message(
                From,
                "😔 I'm having technical difficulties. Please try again in a moment."
            )
        except:
            pass
        
        return Response(content="", media_type="text/plain")


@router.get("/webhook")
async def whatsapp_webhook_verify():
    """Webhook verification endpoint"""
    return {
        "status": "active",
        "service": "WhatsApp AI Companion",
        "message": "Webhook is operational"
    }


@router.post("/send-proactive")
async def send_proactive_message(
    phone_number: str,
    message: str,
    api_key: Optional[str] = None
):
    """
    Send proactive WhatsApp message (for admin/system use)
    Requires API key for security
    """
    # Verify API key
    admin_key = os.getenv("ADMIN_API_KEY")
    if not admin_key or api_key != admin_key:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        success = await whatsapp_companion_service.send_message(
            to_number=phone_number,
            message=message
        )
        
        return {
            "success": success,
            "message": "Message sent" if success else "Failed to send"
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Proactive message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_whatsapp_stats():
    """Get WhatsApp usage statistics"""
    try:
        from app.redis_cache import redis_cache
        
        total_received = redis_cache.get("analytics", "whatsapp:message_received:total") or 0
        total_sent = redis_cache.get("analytics", "whatsapp:message_sent:total") or 0
        new_users = redis_cache.get("analytics", "whatsapp:new_user:total") or 0
        
        return {
            "success": True,
            "stats": {
                "messages_received": total_received,
                "messages_sent": total_sent,
                "new_users": new_users,
                "configured": whatsapp_companion_service.is_configured()
            }
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}
