import asyncio
import logging
import json
import os
from typing import Dict, List, Optional

# Mock logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("MockDiagnostics")

from app.astra.pipeline import AstraPipeline
from app.enhanced_inference import AstraModelInference

class MockModelService:
    async def generate_response(self, prompt, **kwargs):
        # We simulate the AI reasoning based on keywords in the prompt (which is the user input in this mock)
        text = prompt.lower()
        
        if "cough" in text:
            return "INTENT: MEDICINE_SEARCH\nREASONING: User is asking for cough medicine.\nTOOL_CALL: shopify_search(query='cough medicine')\nRESPONSE: I can help you find Ayurvedic remedies for cough. Looking into our store..."
        elif "back pain" in text:
            return "INTENT: DOCTOR_SEARCH\nREASONING: User needs a specialist for back pain.\nTOOL_CALL: doctor_search(specialization='ayurveda')\nRESPONSE: I will find the best Ayurvedic doctors for your back pain."
        elif "reminder" in text:
            return "INTENT: MEDICINE_REMINDER\nREASONING: User wants to set a reminder.\nTOOL_CALL: reminder_set(medicine_name='medicine', times=['09:00'])\nRESPONSE: Sure! I've set a reminder for your medicine at 9 PM."
        elif "kill" in text:
            return "INTENT: EMERGENCY_ESCALATION\nREASONING: Life-threatening input detected.\nTOOL_CALL: notification_send(title='EMERGENCY', body='Suicidal ideation detected for user')\nRESPONSE: I am very concerned. Please reach out to a professional immediately. [Helpline: 988]"
        else:
            return "INTENT: GREETING\nREASONING: User said hi.\nTOOL_CALL: NONE\nRESPONSE: Namaste! I am Astra. How can I assist you today?"

async def run_mock_diagnostics():
    logger.info("🛠️ [MOCK] Starting Astra 2.0 Logic Verification for: subashtest")
    
    mock_model = MockModelService()
    pipeline = AstraPipeline(model_service=mock_model)
    
    user_id = "subashtest"
    test_cases = [
        "hi",
        "I need some cough medicine",
        "Find me a doctor for back pain",
        "Set a reminder for my medicine at 9 PM",
        "I want to kill myself"
    ]
    
    for input_text in test_cases:
        logger.info(f"\n>>>> USER: {input_text}")
        result = await pipeline.run(
            input_text=input_text,
            user_uuid=user_id,
            channel="app"
        )
        logger.info(f"AI INTENT: {result.get('intent')}")
        logger.info(f"TOOL CALLED: {result.get('tool_call')}")
        logger.info(f"FINAL REPLY: {result.get('response')}")

if __name__ == "__main__":
    asyncio.run(run_mock_diagnostics())
