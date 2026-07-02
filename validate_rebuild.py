
import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RebuildValidator")

async def test_rebuild():
    logger.info("🚀 Starting Comprehensive Logic Validation...")
    errors = []

    # 1. Component Import Test
    try:
        from app.astra.pipeline import AstraPipeline
        from app.astra.memory import RAGMemory
        from app.astra.consent import ConsentManager
        from app.astra.routes import initialize_astra_routes
        from app.enhanced_inference import AstraModelInference
        logger.info("✅ Core modules imported successfully")
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        errors.append(f"Import Error: {e}")
        return

    # 2. Pipeline Logic Test (Mocked Network)
    try:
        pipeline = AstraPipeline(inference=MagicMock())
        
        # Mock httpx.AsyncClient to avoid real network call
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value.status_code = 200
            mock_client.post.return_value.json.return_value = {"response": "Success from AI"}
            mock_client.__aenter__.return_value = mock_client
            mock_client_cls.return_value = mock_client

            response = await pipeline.process_query(
                user_id="test_user", 
                message="Hello", 
                history=[]
            )
            
            if response == "Success from AI":
                logger.info("✅ AstraPipeline processed query correctly")
            else:
                msg = f"❌ AstraPipeline unexpected response: {response}"
                logger.error(msg)
                errors.append(msg)

    except Exception as e:
        msg = f"❌ AstraPipeline logic error: {e}"
        logger.error(msg)
        errors.append(msg)

    # 3. Memory Test
    try:
        memory = RAGMemory(max_history=2)
        memory.add_message("user1", "user", "msg1")
        memory.add_message("user1", "assistant", "resp1")
        memory.add_message("user1", "user", "msg2") # Should preserve this
        memory.add_message("user1", "assistant", "resp2") # And this
        
        hist = memory.get_history("user1")
        if len(hist) == 2 and hist[0]['content'] == "msg2":
            logger.info("✅ RAGMemory rolling window works")
        else:
            msg = f"❌ RAGMemory logic failure: {hist}"
            logger.error(msg)
            errors.append(msg)
            
    except Exception as e:
        msg = f"❌ Memory logic error: {e}"
        logger.error(msg)
        errors.append(msg)

    # 4. Legacy Wrapper Test
    try:
        wrapper = AstraModelInference()
        # Mock the internal pipeline of the wrapper
        wrapper.pipeline = MagicMock()
        wrapper.pipeline.process_query.return_value = "Wrapper Success"
        
        resp = await wrapper.generate_response("prompt")
        
        if resp == "Wrapper Success":
            logger.info("✅ AstraModelInference wrapper works")
        else:
            msg = "❌ AstraModelInference failed to delegate"
            logger.error(msg)
            errors.append(msg)

    except Exception as e:
        msg = f"❌ Wrapper logic error: {e}"
        logger.error(msg)
        errors.append(msg)

    # 5. Initialization Test
    try:
        from app.astra.routes import router, pipeline_instance
        # Simulate initialization
        initialize_astra_routes(
            pipeline=AstraPipeline(inference=MagicMock()),
            capability=None,
            consent=ConsentManager(),
            memory=RAGMemory(),
            limiter=None
        )
        # Check global state in routes
        from app.astra.routes import pipeline_instance as checked_instance
        if checked_instance is not None:
            logger.info("✅ Route initialization injection works")
        else:
            msg = "❌ Route global instance injection failed"
            logger.error(msg)
            errors.append(msg)
            
    except Exception as e:
        msg = f"❌ Initialization logic error: {e}"
        logger.error(msg)
        errors.append(msg)

    if not errors:
        logger.info("\n🎉 AUTOMATED VALIDATION PASSED: SYSTEM IS INTERNALLY CONSISTENT")
    else:
        logger.error(f"\n⚠️ FOUND {len(errors)} ERRORS")
        for e in errors:
            logger.error(f"- {e}")

if __name__ == "__main__":
    asyncio.run(test_rebuild())
