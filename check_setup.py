
import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SetupCheck")

async def check_connection():
    logger.info("--- checking api.ayureze.in connection ---")
    try:
        from app.enhanced_inference import AstraModelInference
        inference = AstraModelInference()
        await inference.load_model()
        
        logger.info("Attempting to generate response from real API...")
        # Use a simpler prompt
        response = await inference.generate_response("hi", language="en")
        logger.info(f"✅ API Response received: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ API Connection Failed: {e}")
        return False

def check_pipeline_init():
    logger.info("--- checking AstraPipeline initialization ---")
    try:
        from app.astra.pipeline import AstraPipeline
        # We now verify that it requires an argument or we pass one
        try:
             # This SHOULD fail if we don't pass arg, but let's try to pass one to be sure it works WITH one
            from app.enhanced_inference import AstraModelInference
            inf = AstraModelInference()
            p = AstraPipeline(inference=inf)
            logger.info("✅ Successfully initialized AstraPipeline(inference=...)")
            return True
        except TypeError as e:
             logger.error(f"❌ Failed to init AstraPipeline even with arg: {e}")
             return False
    except Exception as e:
        logger.error(f"❌ Other error initializing AstraPipeline: {e}")
        return False

async def main():
    # Run pipeline check first as it is fast
    pipeline_ok = check_pipeline_init()
    
    # Run connection check
    connection_ok = await check_connection()
    
    if connection_ok and pipeline_ok:
        logger.info("\n🎉 ALL CHECKS PASSED")
    else:
        logger.error("\n❌ CHECKS FAILED")
        if not pipeline_ok: logger.error("- Pipeline Init Failed")
        if not connection_ok: logger.error("- API Connection Failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
