
"""
Custom WhatsApp Webhook Handler - Astra Rebuild
"""

from fastapi import APIRouter, Request, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.get("/custom-whatsapp")
async def webhook_health():
    return {
        "status": "active",
        "service": "Custom WhatsApp Webhook - Astra Rebuild",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/custom-whatsapp")
async def receive_whatsapp(
    request: Request,
    background_tasks: BackgroundTasks
):
    try:
        raw = await request.body()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = dict(await request.form())

        # 🔒 LOOP PREVENTION
        if (
            payload.get("from_me") is True
            or payload.get("isBot") is True
            or payload.get("direction") == "outgoing"
            or payload.get("sender") in ("system", "bot")
        ):
            logger.info("Ignored outgoing/bot WhatsApp message")
            return {"success": True, "ignored": True}

        background_tasks.add_task(process_message, payload)
        return {"success": True}

    except Exception as e:
        logger.exception("Webhook receive failed")
        return {"success": False, "error": str(e)}

async def process_message(data: Dict[str, Any]):
    try:
        logger.info(f"Incoming WhatsApp payload: {data}")

        # Normalization
        contact = data.get("contact", {})
        message = data.get("message", {})

        phone = (
            contact.get("phone_number")
            or data.get("phone")
            or data.get("From")
            or data.get("wa_id")
            or data.get("sender")
        )

        text = (
            message.get("body")
            or data.get("body")
            or data.get("message")
            or data.get("text")
        )

        if not phone or not text:
            return

        phone = str(phone).replace("whatsapp:", "").strip()
        text_clean = str(text).strip()

        # Import global instances from Astra routes
        from app.astra.routes import pipeline_instance, rag_memory_instance
        from app.medicine_reminders.custom_whatsapp_client import CustomWhatsAppClient

        if not pipeline_instance or not rag_memory_instance:
            logger.error("Astra Core Components not ready - skipping WhatsApp message")
            return
            
        # 1. Fetch History
        history = rag_memory_instance.get_history(phone)
        
        # 2. Process with Astra AI (The ONLY intelligence source)
        ai_response_text = await pipeline_instance.process_query(
            user_id=phone,
            message=text_clean,
            history=history
        )
        
        # 3. Update Memory
        rag_memory_instance.add_message(phone, "user", text_clean)
        rag_memory_instance.add_message(phone, "assistant", ai_response_text)

        # 4. Send Response
        # We explicitly use the AI text. No fallbacks.
        if ai_response_text:
            client = CustomWhatsAppClient()
            # Assuming send_text_message is async
            await client.send_text_message(phone, ai_response_text)

    except Exception as e:
        logger.exception(f"Error processing WhatsApp message: {e}")
