import asyncio
import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.enhanced_inference import AstraModelInference
from app.astra.pipeline import AstraPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)

async def run_test():
    print(">>> Starting Astra Connectivity Test...")
    
    # Test 1: Direct Inference
    print("\n--- TEST 1: Direct Model Inference ---")
    inference = AstraModelInference()
    await inference.load_model()
    
    test_query = "Describe the benefits of Ashwagandha."
    print(f"Sending Query: '{test_query}'")
    
    try:
        response = await inference.generate_response(test_query)
        print("\n[SUCCESS] Model Response Received:")
        print(f"'{response}'")
    except Exception as e:
        print(f"\n[ERROR] Inference Error: {repr(e)}")
        import traceback
        traceback.print_exc()
        inference.cleanup()
        return

    # Test 2: Pipeline
    print("\n--- TEST 2: Astra Pipeline Flow ---")
    pipeline = AstraPipeline(inference)
    try:
        # Re-using the loaded inference
        pipeline_response = await pipeline.run("How do I take Triphala?", "en")
        print("\n[SUCCESS] Pipeline Response Received:")
        print(f"'{pipeline_response}'")
    except Exception as e:
        print(f"\n[ERROR] Pipeline Error: {e}")
    
    inference.cleanup()
    print("\n>>> Test Complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
