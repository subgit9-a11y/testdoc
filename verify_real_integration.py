import asyncio
import sys
import os
import logging

# Ensure we can import from the project root
sys.path.append(os.getcwd())

# Configuration: We want to test REAL connectivity, not mocks
os.environ["BRAIN_API_PREFIX"] = "https://api.ayureze.in"

async def verify_real_integration():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RealIntegrationTest")
    
    logger.info("Starting REAL AI Integration Test (No Mocks)")
    
    try:
        from app.astra_brain_client import AstraBrainClient
        client = AstraBrainClient()
        
        # 1. Health Check
        logger.info("Checking remote health...")
        health = await client.check_health()
        logger.info(f"Health Status: {health}")
        
        if health.get("status") != "online":
            logger.error("Remote Brain is NOT online. Ending test.")
            return

        # 2. Real Chat
        logger.info("Sending REAL query to api.ayureze.in...")
        response = await client.chat("Summarize the benefits of Triphala in 2 sentences.")
        
        if response.success:
            logger.info("✅ SUCCESS: Received response from remote brain.")
            logger.info(f"Answer: {response.answer}")
        else:
            logger.error(f"❌ FAILED: {response.answer}")

        # 3. Real Autopilot
        logger.info("Testing Autopilot Routing...")
        auto = await client.autopilot("I want to buy some herbal supplements")
        logger.info(f"Detected Intent: {auto.intent}")
        
        # 4. Real Safety
        logger.info("Testing Safety Sentinel...")
        safety = await client.analyze_safety("Is it safe to consume honey with hot water?")
        logger.info(f"Safety Analysis: Is Safe? {safety.is_safe}, Risk: {safety.risk_level}")

        await client.close()
        logger.info("Test Completed.")
        
    except Exception as e:
        logger.error(f"Test crashed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(verify_real_integration())
