
import asyncio
import logging
from unittest.mock import MagicMock, patch

# Configure logging to flush immediately
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("LightValidator")

async def test_light():
    logger.info("🚀 Starting Light Validation (Astra Core Only)...")
    
    # 1. Test Astra Modules isolated from Main
    try:
        from app.astra.pipeline import AstraPipeline
        from app.astra.memory import RAGMemory
        from app.astra.routes import router
        logger.info("✅ Astra modules imported cleanly")
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return

    # 2. Test Pipeline Logic
    try:
        pipeline = AstraPipeline()
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value.status_code = 200
            mock_client.post.return_value.json.return_value = {"answer": "Astra Online"}
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            
            res = await pipeline.process_query("u1", "hi", [])
            if res == "Astra Online":
                logger.info("✅ Pipeline logic verified")
            else:
                logger.error(f"❌ Pipeline returned unexpected: {res}")
    except Exception as e:
        logger.error(f"❌ Pipeline broke: {e}")

    logger.info("🎉 Light Validation Complete")

if __name__ == "__main__":
    asyncio.run(test_light())
