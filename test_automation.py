
import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutomationCheck")

async def test_automation_flow():
    from app.astra.capabilities import CapabilityAgent
    from app.astra.pipeline import AstraPipeline

    logger.info("--- Testing Automation & Escalation Flow ---")
    
    # Setup
    agent = CapabilityAgent()
    inference_mock = MagicMock()
    pipeline = AstraPipeline(inference_mock, agent)

    # 1. Test Regular Response
    logger.info("1. Testing Regular Response...")
    inference_mock.generate_response.return_value = "Hello, I can help you."
    resp1 = await pipeline.process_query("u1", "hi", [])
    if resp1 == "Hello, I can help you.":
        logger.info("✅ Regular pass-through working")
    else:
        logger.error(f"❌ Regular response failed: {resp1}")

    # 2. Test Escalation
    logger.info("2. Testing Escalation Trigger...")
    inference_mock.generate_response.return_value = "I am unsure. [ESCALATE] Please wait for a human."
    resp2 = await pipeline.process_query("u1", "help me now", [])
    if "[ESCALATE]" not in resp2:
        logger.info("✅ Escalation tag correctly stripped/handled")
        logger.info(f"   Response output: '{resp2}'")
    else:
        logger.error("❌ Escalation tag was NOT stripped")

    # 3. Test Action/Tool Call
    logger.info("3. Testing Tool Execution...")
    # Simulate LLaMA outputting a JSON action
    action_json = '{"tool": "book_appointment", "data": {"date": "Monday"}}'
    inference_mock.generate_response.return_value = f"Booking now... [ACTION:{action_json}]"
    
    resp3 = await pipeline.process_query("u1", "book for monday", [])
    if "Appointment successfully booked" in resp3:
         logger.info("✅ Tool execution successful")
         logger.info(f"   Final Result: '{resp3}'")
    else:
         logger.error(f"❌ Tool execution failed. Got: {resp3}")

if __name__ == "__main__":
    asyncio.run(test_automation_flow())
