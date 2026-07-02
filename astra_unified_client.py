
"""
Astra Unified AI Client - Advanced Integration for Healthcare Services
Version: 3.1.0
Supports: Brain Chat, Fill, Autopilot, Wellness, Analysis, Doctor Summary, Shop Assist, Schedule
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AstraUnifiedClient:
    def __init__(self, base_url: str = "https://metal-rotary-nano-heavily.trycloudflare.com"):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(120.0, read=120.0, connect=10.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.client.post(f"{self.base_url}{path}", json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API Error ({path}): {response.status_code} - {response.text}")
                return {"error": f"Status {response.status_code}", "detail": response.text}
        except Exception as e:
            logger.error(f"Network Error ({path}): {e}")
            return {"error": "Network Error", "detail": str(e)}

    async def _get(self, path: str) -> Dict[str, Any]:
        try:
            response = await self.client.get(f"{self.base_url}{path}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    # Core Intelligence
    async def chat(self, query: str, session_id: Optional[str] = None, history: Optional[List[Dict[Any, Any]]] = None) -> str:
        payload = {
            "query": query,
            "session_id": session_id,
            "messages": history or []
        }
        res = await self._post("/api/v1/brain/chat", payload)
        return res.get("answer", res.get("response", "No response from Astra Brain."))

    # Wellness
    async def generate_wellness(self, topic: str, duration: str = "5 minutes") -> str:
        payload = {"topic": topic, "duration": duration}
        res = await self._post("/api/v1/brain/generate-wellness", payload)
        return res.get("wellness_plan", res.get("response", "Could not generate wellness plan."))

    # Clinical Analysis
    async def analyze_clinical(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        payload = {"text": text, "analysis_type": analysis_type}
        return await self._post("/api/v1/brain/detect-emotion" if analysis_type == "emotion" else "/api/v1/analyze", payload)

    async def doctor_summary(self, notes: str, output_format: str = "summary") -> str:
        payload = {"notes": notes, "output_format": output_format}
        res = await self._post("/api/v1/brain/doctor-summary", payload)
        return res.get("summary", res.get("response", "Could not generate summary."))

    # Automation & Intent
    async def autopilot(self, query: str, actions: Optional[List[str]] = None) -> Dict[str, Any]:
        payload = {"query": query, "available_actions": actions or []}
        return await self._post("/api/v1/brain/autopilot", payload)

    # Extraction
    async def extract_info(self, text: str, schema: str = "{}") -> Dict[str, Any]:
        payload = {"text": text, "schema_definition": schema}
        return await self._post("/api/v1/brain/fill", payload)

    async def extract_schedule(self, prescription_text: str) -> Dict[str, Any]:
        payload = {"prescription_text": prescription_text}
        return await self._post("/api/v1/brain/extract-schedule", payload)

    # E-commerce Support
    async def shop_assist(self, query: str) -> Dict[str, Any]:
        payload = {"query": query}
        return await self._post("/api/v1/brain/shop-assist", payload)

    # Utility
    async def check_health(self) -> bool:
        res = await self._get("/api/v1/brain/health")
        return "error" not in res

    async def close(self):
        await self.client.aclose()

# Singleton instance for global use
astra_ai = AstraUnifiedClient()
