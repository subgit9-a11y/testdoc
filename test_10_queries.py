import asyncio
import logging
import os
from dotenv import load_dotenv
from app.astra_brain_client import AstraBrainClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QueryTester")

async def run_10_queries():
    load_dotenv()
    client = AstraBrainClient()
    
    queries = [
        "What is Triphala Choornam and how to take it?",
        "How to balance Vata Dosha through diet?",
        "Ayurvedic suggestions for chronic insomnia/better sleep?",
        "Best herbs for improving digestive health (Agni)?",
        "How should I consume Ashwagandha for stress relief?",
        "Natural Ayurvedic remedies for common cold and cough?",
        "Explain the characteristics of Pitta constitution.",
        "Ayurvedic tips for glowing skin and anti-aging?",
        "Scientific and traditional benefits of Turmeric (Haridra)?",
        "Ideal daily routine (Dinacharya) for Kapha Dosha?"
    ]
    
    print("\n" + "="*80)
    print("Astra AI - 10 Query Response Test (api.ayureze.in)")
    print("="*80)
    
    results = []
    for i, q in enumerate(queries, 1):
        print(f"\n[{i}/10] Query: {q}")
        try:
            # Using chat endpoint which gives natural language answers
            resp = await client.chat(q)
            if resp.success:
                print(f"--- Response ---\n{resp.answer}\n-----------------")
                results.append({"query": q, "status": "SUCCESS", "answer": resp.answer})
            else:
                print(f"--- FAILED: {resp.answer} ---")
                results.append({"query": q, "status": "FAIL", "error": resp.answer})
        except Exception as e:
            print(f"--- EXCEPTION: {e} ---")
            results.append({"query": q, "status": "ERROR", "error": str(e)})
        
        # Small delay to be polite to the backend
        await asyncio.sleep(1)

    print("\n" + "="*80)
    print("Test Summary:")
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"Total Success: {success_count}/10")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_10_queries())
