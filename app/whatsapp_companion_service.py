"""
WhatsApp Service for AI Companion
Production-ready WhatsApp integration
"""

import os
import logging
from typing import Optional, List
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WhatsAppCompanionService:
    """WhatsApp integration for AI Companion"""
    
    def __init__(self):
        # Twilio configuration
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        self.client = None
        self.mode = "disabled"
        
        if self.account_sid and self.auth_token:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                self.mode = "twilio"
                logger.info("✅ WhatsApp service initialized (Twilio)")
            except ImportError:
                logger.warning("⚠️ twilio library not installed. Run: pip install twilio")
            except Exception as e:
                logger.error(f"Twilio initialization error: {e}")
        else:
            logger.info("💬 WhatsApp not configured (will work in test mode)")
    
    async def send_message(
        self,
        to_number: str,
        message: str,
        timeout: float = 30.0
    ) -> bool:
        """
        Send WhatsApp message with timeout
        
        Args:
            to_number: Phone number (e.g., '+919876543210' or 'whatsapp:+919876543210')
            message: Text message
            timeout: Request timeout in seconds
        """
        if not self.client:
            logger.warning(f"WhatsApp not configured. Would send: {message[:50]}")
            return False
        
        try:
            # Format phone number
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            # Simulated typing delay for better UX
            import random
            typing_delay = 0.8 + (random.random() * 1.2) # 0.8 to 2.0 seconds
            logger.info(f"⏳ Simulating typing for {typing_delay:.2f}s...")
            await asyncio.sleep(typing_delay)
            
            # Send with timeout wrapper
            result = await asyncio.wait_for(
                self._send_message_sync(to_number, message),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"WhatsApp send timeout for {to_number}")
            return False
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return False
    
    async def _send_message_sync(self, to_number: str, message: str) -> bool:
        """Synchronous send wrapped for async"""
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            logger.info(f"✅ WhatsApp sent: {msg.sid}")
            return True
        except Exception as e:
            logger.error(f"Twilio API error: {e}")
            return False
    
    async def send_document(
        self,
        to_number: str,
        document_url: str,
        caption: Optional[str] = None
    ) -> bool:
        """
        Send document (PDF, image, etc.) via WhatsApp
        
        Args:
            to_number: Phone number
            document_url: Publicly accessible URL of document
            caption: Optional message with document
        """
        if not self.client:
            logger.warning("WhatsApp not configured")
            return False
        
        try:
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            msg = self.client.messages.create(
                from_=self.whatsapp_number,
                to=to_number,
                body=caption or "📄 Document attached",
                media_url=[document_url]
            )
            
            logger.info(f"✅ Document sent: {msg.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Document send error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if WhatsApp is properly configured"""
        return self.client is not None

# Global instance
whatsapp_companion_service = WhatsAppCompanionService()
