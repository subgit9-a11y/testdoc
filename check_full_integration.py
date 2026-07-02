
import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock, AsyncMock

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FullIntegrationCheck")

async def check_full_stack():
    logger.info("--- 1. Checking Chat Pipeline ---")
    from app.astra.pipeline import AstraPipeline
    
    # Use AsyncMock for awaitable methods
    inference_mock = AsyncMock()
    inference_mock.generate_response.return_value = "Mocked Response"
    
    pipeline = AstraPipeline(inference=inference_mock)
    
    # Test Run alias (Autopilot uses this)
    await pipeline.run("test", user_uuid="123")
    logger.info("✅ Pipeline 'run' alias works (Autopilot ready)")

    logger.info("--- 2. Checking Astra Fill Connection ---")
    from app.model_service import ModelService
    
    # Verify we can set the inference engine
    ModelService.set_model_inference(inference_mock)
    
    # Test generate response via Service (calls with context kwarg)
    resp = await ModelService.get_instance().generate_response("patient prompt", context="medical_history")
    
    # Verify mock was called
    if inference_mock.generate_response.call_count >= 2:
        logger.info("✅ ModelService is successfully routing to Inference Engine")
    else:
        logger.error("❌ ModelService did not call Inference Engine")

if __name__ == "__main__":
    asyncio.run(check_full_stack())
