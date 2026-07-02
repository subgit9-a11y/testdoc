
"""
Astra AI Client - Connects to the Central Intelligence Server (Astra Companion)
Version: 3.1.0
"""

import logging
import httpx
import os
import asyncio
from typing import Optional
from astra_unified_client import AstraUnifiedClient

logger = logging.getLogger(__name__)

class AstraClient:
    def __init__(self, api_url: str = "https://metal-rotary-nano-heavily.trycloudflare.com"):
        self.api_endpoint = api_url.rstrip("/")
        self.loaded = False
        self.timeout = httpx.Timeout(120.0, read=120.0, connect=10.0)
        self.unified = AstraUnifiedClient(self.api_endpoint)

    async def load_model(self):
        """
        Verifies connection to the remote AI Brain.
        """
        logger.info(f"⏳ Connecting to Astra Brain at {self.api_endpoint}...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to hit health endpoint if it exists, otherwise assume online if URL is valid
                # The guide specifies a /health endpoint on the server side code
                resp = await client.get(f"{self.api_endpoint}/health")
                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"✅ Astra Brain Online: {data}")
                    self.loaded = True
                else:
                    logger.warning(f"⚠️ Astra Brain returned {resp.status_code} on health check. Assuming active for /ask.")
                    self.loaded = True
                    
        except Exception as e:
            logger.error(f"❌ Failed to reach Astra Brain: {e}")
            logger.info("⚠️ Proceeding, but AI requests may fail if server is down.")
            # We mark as loaded anyway so the app doesn't crash on startup, 
            # but individual requests will fail if still down.
            self.loaded = True 

    def is_loaded(self) -> bool:
        return self.loaded

    async def generate_response(self, prompt: str, language: str = "en", context: Optional[str] = None) -> str:
        """
        Sends the prompt to the remote AI model and retrieves the answer.
        """
        if not self.loaded:
            # Try to lazy load or just fail
            logger.warning("Astra Client not explicitly loaded, assuming ready.")
        
        # Prepend context if provided (for compatibility)
        if context:
            prompt = f"Context: {context}\n{prompt}"

        # Spec expects {"q": "string"} for /v1/chat
        # New unified backend supports /api/v1/brain/chat as preferred
        payload = {
            "query": prompt,
            "language": language
        }

        try:
            # Try new unified method first
            answer = await self.unified.chat(prompt)
            if answer and "[ESCALATE]" not in answer:
                return answer
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_endpoint}/v1/chat",
                    json={"q": prompt}
                )

            if response.status_code != 200:
                logger.error(f"❌ AI Server Error ({response.status_code}): {response.text}")
                return "I am currently having trouble connecting to my brain. Please try again later. [ESCALATE]"

            data = response.json()
            
            # Validation - Handles 'answer' or 'response' keys
            raw_answer = data.get("answer", data.get("response", "")) or "No response from AI brain."
                
            return str(raw_answer).replace("[SYSTEM]:", "").strip()

        except httpx.RequestError as e:
            logger.error(f"❌ Network Error connecting to AI: {e}")
            return "My connection to the cloud is weak. Please check your internet. [ESCALATE]"
        except Exception as e:
            logger.error(f"❌ Unexpected Error in AstraClient: {e}")
            return "I encountered a system error. [ESCALATE]"

    def cleanup(self):
        logger.info("AstraClient shutdown.")