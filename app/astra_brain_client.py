"""
Astra Brain Client - Unified API Connector for Astra Companion
Version: 4.2.1 - Robust Client pooling & Unified Extraction
"""

import logging
import httpx
import asyncio
import json
import re
import os
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class Intent(Enum):
    CHAT = "chat"
    BOOKING = "booking"
    PROFILE = "profile"
    HISTORY = "history"

@dataclass
class ChatResponse:
    answer: str
    mode: str
    success: bool = True

@dataclass
class AutopilotResponse:
    intent: Intent
    status: str
    confidence: float = 1.0

@dataclass
class SafetyAnalysis:
    is_safe: bool
    flags: List[str]
    risk_level: str = "low"

@dataclass
class EmotionResult:
    emotion: str
    intensity: str
    confidence: float = 0.8

@dataclass
class ScheduleResult:
    reminders: List[Dict[str, Any]]
    raw_json: str

# ============================================================================
# Main Client
# ============================================================================

class AstraBrainClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.getenv("BRAIN_API_PREFIX", "https://metal-rotary-nano-heavily.trycloudflare.com")).rstrip("/")
        # New base prefix based on the OpenAPI spec
        self.api_prefix = self.base_url
        
        # Optimize performance: reuse HTTP connection pools and longer timeout
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
        self.timeout = httpx.Timeout(120.0, read=120.0, connect=10.0)
        
        self.client = httpx.AsyncClient(timeout=self.timeout, limits=limits)
        self._connected = False
        
        # JWT Master Token State
        self.jwt_token = None
        self.token_expiry = 0
        
        logger.info(f"\ud83e\udde0 AstraBrainClient optimized and initialized \u2192 {self.api_prefix}")

    async def _ensure_authenticated(self):
        """Fetches a Master JWT Token if missing or expired (older than 23 hours)"""
        current_time = time.time()
        # Refresh token if it doesn't exist or is older than 23 hours (82800 seconds)
        if not self.jwt_token or current_time > self.token_expiry:
            try:
                auth_url = f"{self.api_prefix}/api/v1/auth/session?user_id=companion_master"
                response = await self.client.post(auth_url)
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data.get("session_token")
                    self.token_expiry = current_time + 82800 # Good for 23 hours
                    logger.info("✅ AstraBrainClient successfully fetched new Master JWT Token")
                else:
                    logger.error(f"❌ Failed to fetch Master JWT Token: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Exception fetching Master JWT Token: {e}")
                
    def _get_headers(self) -> Dict[str, str]:
        """Returns the headers including the JWT token"""
        if self.jwt_token:
            return {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    async def close(self):
        """Clean up connections on shutdown"""
        await self.client.aclose()

    async def check_health(self) -> Dict[str, Any]:
        try:
            # Reusing client
            response = await self.client.get(f"{self.api_prefix}/health")
            if 200 <= response.status_code < 300:
                self._connected = True
                return {"status": "online"}
            return {"status": "degraded", "code": response.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    async def chat(self, query: str) -> ChatResponse:
        try:
            await self._ensure_authenticated()
            # Server expects ChatRequest: {"query": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/chat", json={"query": query}, headers=self._get_headers())
            if response.status_code != 200:
                logger.error(f"❌ Chat API Failed: {response.status_code} {response.text}")
                return ChatResponse(answer="API error", mode="error", success=False)
                
            data = response.json()
            # The server returns "answer" directly or in "choices"
            raw_answer = data.get("answer", "")
            if not raw_answer and "choices" in data:
                raw_answer = data["choices"][0]["message"]["content"]
            
            raw_answer = raw_answer or "No response from AI brain."
            return ChatResponse(
                answer=raw_answer.replace("[SYSTEM]:", "").strip(),
                mode=data.get("mode", "chat"),
                success=True
            )
        except Exception as e:
            logger.error(f"❌ Chat API Exception: {e}")
            return ChatResponse(answer="I'm having trouble connecting to the brain.", mode="error", success=False)

    async def chat_stream(self, query: str):
        """Stream the AI response from the GPU Server"""
        try:
            await self._ensure_authenticated()
            # Request streaming explicitly
            async with self.client.stream("POST", f"{self.api_prefix}/v1/chat", json={"query": query}, headers=self._get_headers()) as response:
                if response.status_code != 200:
                    logger.error(f"❌ Chat Stream API Failed: {response.status_code}")
                    yield f"data: {json.dumps({'error': 'API Error'})}\n\n"
                    return
                async for chunk in response.aiter_text():
                    yield chunk
        except Exception as e:
            logger.error(f"❌ Chat Stream Exception: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    async def autopilot(self, query: str) -> AutopilotResponse:
        try:
            await self._ensure_authenticated()
            # Server expects AutopilotRequest: {"query": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/autopilot", json={"query": query}, headers=self._get_headers())
            data = response.json()
            
            # The brain returns the result in "result" or "decision"
            intent_str = str(data.get("result", data.get("intent", "CHAT"))).lower()
            
            # Heuristic for intent detection
            if any(word in intent_str for word in ["book", "appointment", "doctor", "schedule", "physician"]):
                intent = Intent.BOOKING
            elif any(word in intent_str for word in ["profile", "my info", "account"]):
                intent = Intent.PROFILE
            elif any(word in intent_str for word in ["prescription", "history", "records", "report"]):
                intent = Intent.HISTORY
            else:
                intent = Intent.CHAT
                
            return AutopilotResponse(intent=intent, status="success")
        except Exception:
            return AutopilotResponse(intent=Intent.CHAT, status="error")

    async def fill(self, text: str, schema_definition: str) -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects FillRequest: {"text": "string", "schema_definition": "string"}
            response = await self.client.post(
                f"{self.api_prefix}/v1/fill", 
                json={"text": text, "schema_definition": schema_definition},
                headers=self._get_headers()
            )
            data = response.json()
            extracted_data = data.get("extracted_data", data)
            
            return {"success": response.status_code == 200, "extracted_data": extracted_data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def shop_assist(self, query: str) -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects ShopRequest: {"query": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/shop_assist", json={"query": query}, headers=self._get_headers())
            return {"success": response.status_code == 200, "result": response.json().get("result", "{}")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def extract_schedule(self, text: str) -> ScheduleResult:
        try:
            await self._ensure_authenticated()
            # Server expects ScheduleRequest: {"prescription_text": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/extract_schedule", json={"prescription_text": text}, headers=self._get_headers())
            if response.status_code != 200:
                return ScheduleResult(reminders=[], raw_json=f"HTTP {response.status_code}")
                
            res = response.json()
            raw_schedule = res.get("schedule", "")
            
            # Extraction logic for Markdown JSON
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_schedule, re.DOTALL)
            extracted_str = json_match.group(1) if json_match else raw_schedule
            
            try:
                parsed = json.loads(extracted_str)
                reminders = []
                if isinstance(parsed, dict):
                    if "reminders" in parsed: reminders = parsed["reminders"]
                    elif "Reminder" in parsed: reminders = [parsed["Reminder"]]
                    else: reminders = [parsed]
                elif isinstance(parsed, list):
                    reminders = parsed
                
                return ScheduleResult(reminders=reminders, raw_json=json.dumps(parsed))
            except:
                return ScheduleResult(reminders=[], raw_json=raw_schedule)
        except Exception as e:
            logger.error(f"❌ Extraction API Failed: {e}")
            return ScheduleResult(reminders=[], raw_json=str(e))

    async def doctor_summary(self, patient_notes: str) -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects DoctorRequest: {"notes": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/doctor_summary", json={"notes": patient_notes}, headers=self._get_headers())
            if response.status_code != 200:
                return {"success": False, "error": f"API Error {response.status_code}"}
            
            data = response.json()
            summary = data.get("summary", data.get("clinical_summary", "")) or "Clinical summary not available."
            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def analyze_safety(self, user_text: str) -> SafetyAnalysis:
        try:
            await self._ensure_authenticated()
            # Server expects AnalyzeRequest: {"text": "string", "analysis_type": "safety"}
            response = await self.client.post(
                f"{self.api_prefix}/v1/analyze_safety", 
                json={"text": user_text, "analysis_type": "safety"},
                headers=self._get_headers()
            )
            if response.status_code != 200:
                return SafetyAnalysis(is_safe=True, flags=[], risk_level="unknown")
            
            data = response.json()
            result_text = data.get("result", "")
            
            # Default to safe if we can't parse it
            is_safe = True
            flags = []
            risk_level = "low"
            
            if "unsafe" in result_text.lower() or "risk" in result_text.lower():
                is_safe = False
                risk_level = "high"
                flags.append("Potential medical risk detected")

            return SafetyAnalysis(is_safe=is_safe, flags=flags, risk_level=risk_level)
        except Exception:
            return SafetyAnalysis(is_safe=True, flags=[], risk_level="unknown")

    async def detect_emotion(self, query: str) -> EmotionResult:
        try:
            await self._ensure_authenticated()
            # Server expects AnalyzeRequest: {"text": "string", "analysis_type": "emotion"}
            response = await self.client.post(
                f"{self.api_prefix}/v1/detect_emotion", 
                json={"text": query, "analysis_type": "emotion"},
                headers=self._get_headers()
            )
            if response.status_code != 200:
                return EmotionResult(emotion="Neutral", intensity="Medium")
            
            d = response.json()
            res_text = d.get("result", "Neutral")
            
            return EmotionResult(emotion=res_text, intensity="Medium")
        except Exception:
            return EmotionResult(emotion="Neutral", intensity="Medium")

    async def profile_analysis(self, profile_data_a: str, task: str = "buddy_match", profile_data_b: Optional[str] = None) -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects: {"profile_data_a": "string", "task": "string", "profile_data_b": "string | null"}
            payload = {"profile_data_a": profile_data_a, "task": task, "profile_data_b": profile_data_b}
            response = await self.client.post(f"{self.api_prefix}/v1/profile_analysis", json=payload, headers=self._get_headers())
            return {"success": response.status_code == 200, "analysis": response.json().get("result", "")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_wellness(self, topic: str, duration: str = "5 mins") -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects WellnessRequest: {"topic": "string", "duration": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/generate_wellness", json={"topic": topic, "duration": duration}, headers=self._get_headers())
            if response.status_code != 200:
                return {"success": False, "error": f"API Error {response.status_code}"}
            
            data = response.json()
            content = data.get("content", "")
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def adjust_tone(self, text: str, target_tone: str = "polite") -> Dict[str, Any]:
        try:
            await self._ensure_authenticated()
            # Server expects: {"text": "string", "target_tone": "string"}
            response = await self.client.post(f"{self.api_prefix}/v1/adjust_tone", json={"text": text, "target_tone": target_tone}, headers=self._get_headers())
            if response.status_code != 200:
                return {"success": False, "rewritten_text": text, "error": f"API Error {response.status_code}"}
            
            data = response.json()
            rewritten = data.get("adjusted_text", text)
            return {
                "success": True, 
                "rewritten_text": rewritten
            }
        except Exception as e:
            return {"success": False, "rewritten_text": text, "error": str(e)}


# =========================================================================
# Singleton Instance & Dependency Injection
# =========================================================================

_brain_client = None

def get_brain_client() -> AstraBrainClient:
    """Provides a singleton instance of the AstraBrainClient"""
    global _brain_client
    if _brain_client is None:
        _brain_client = AstraBrainClient()
    return _brain_client

astra_brain = get_brain_client()
