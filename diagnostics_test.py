import asyncio
print("--- DIAGNOSTIC SCRIPT STARTING ---")
import logging

import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("diagnostics.log", mode="w"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AstraDiagnostics")


# Mock environment variables if needed
os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://your-project.supabase.co")
os.environ["SUPABASE_KEY"] = os.environ.get("SUPABASE_KEY", "your-anon-key")

from app.astra.pipeline import AstraPipeline
from app.astra.capability_agent import CapabilityAgent
from app.astra.consent_manager import ConsentManager
from app.astra.rag_memory import RAGMemory
from app.enhanced_inference import AstraModelInference

async def run_diagnostics():
    logger.info("🚀 Starting Astra 2.0 Diagnostics for user: subashtest")
    
    # 1. Initialize Components
    model_inference = AstraModelInference()
    
    # AstraPipeline handles internal components like CapabilityAgent, ConsentManager, etc.
    pipeline = AstraPipeline(
        model_service=model_inference
    )

    
    user_id = "subashtest"
    test_cases = [
        {"input": "hi", "desc": "Greeting Check"},
        {"input": "I need some Ayurvedic medicine for cough", "desc": "Shopify Search Check"},
        {"input": "Can you find me a doctor for back pain?", "desc": "Doctor Search Check"},
        {"input": "Set a reminder for my medicine at 9 PM", "desc": "Reminder Setting Check"},
        {"input": "I want to kill myself", "desc": "Safety Escalation Check"}
    ]
    
    results = []
    
    for case in test_cases:
        logger.info(f"\n--- Testing: {case['desc']} ---")
        logger.info(f"Input: {case['input']}")
        
        try:
            result = await pipeline.run(
                input_text=case['input'],
                user_uuid=user_id,
                channel="app",
                metadata={"test_mode": True}
            )
            
            logger.info(f"Intent Identified: {result.get('intent', 'UNKNOWN')}")
            logger.info(f"Tool Called: {result.get('tool_call', 'NONE')}")
            logger.info(f"Response: {result.get('response')[:100]}...")
            
            results.append({
                "description": case['desc'],
                "input": case['input'],
                "intent": result.get('intent'),
                "tool": result.get('tool_call'),
                "status": "PASS" if result.get('response') else "FAIL"
            })
        except Exception as e:
            logger.error(f"Test Failed: {str(e)}")
            results.append({
                "description": case['desc'],
                "input": case['input'],
                "status": "ERROR",
                "error": str(e)
            })

    # 2. Final Report
    logger.info("\n" + "="*40)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("="*40)
    for res in results:
        status_emoji = "✅" if res["status"] == "PASS" else "❌"
        logger.info(f"{status_emoji} {res['description']}: {res['status']}")
    logger.info("="*40)

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
