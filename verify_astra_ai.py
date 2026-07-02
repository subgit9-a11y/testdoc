import asyncio
import os
import sys
import logging

# Ensure local 'app' is in path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app.astra.pipeline import AstraPipeline
from app.database import db_manager

# Set logging to see details
logging.basicConfig(level=logging.INFO)

async def verify_astra_knowledge():
    print("\n--- [VERIFY] Astra Ayurvedic Knowledge & Supabase Storage ---")
    
    # Check Supabase status
    if not db_manager.is_connected():
        print("[-] Supabase is not connected. Check SUPABASE_URL and SUPABASE_KEY.")
        return
    else:
        print("[+] Supabase connection confirmed.")

    # Initialize memory and consent
    from app.astra.memory import RAGMemory
    from app.astra.consent import ConsentManager
    from app.astra.rate_limit import RateLimiter
    from app.astra.capabilities import CapabilityAgent
    
    memory = RAGMemory()
    consent = ConsentManager()
    limiter = RateLimiter()
    capability = CapabilityAgent()
    
    pipeline = AstraPipeline(capability_agent=capability)
    
    user_id = "test_doctor_verify_001"
    query = "What are the primary symptoms of Kapha Dosha imbalance in Ayurveda?"
    
    print(f"\nQUERY: {query}")
    
    # 1. Process via Pipeline
    response = await pipeline.process_query(
        user_id=user_id,
        message=query,
        history=[]
    )
    
    print(f"\nAI RESPONSE:\n{response}")
    
    # Check if response looks Ayurvedic
    ayurvedic_keywords = ["Kapha", "Dosha", "Ayurveda", "Prakriti", "Agni", "Guna", "herb", "herbal"]
    has_ayurvedic_terms = any(word.lower() in response.lower() for word in ayurvedic_keywords)
    
    if has_ayurvedic_terms:
        print("\n[+] Response contains valid Ayurvedic terminology.")
    else:
        print("\n[?] Warning: Response might lack deep Ayurvedic context.")

    # 2. Check Supabase for the record
    print("\nCHECKING Supabase for conversation record...")
    
    # Manually trigger storage for testing the db_manager directly if pipeline fails
    # (The pipeline should do it automatically now based on our recent changes)
    await asyncio.sleep(2)
    
    history = await db_manager.get_user_chat_history(user_id=user_id, limit=5)
    
    if history:
        latest = history[0]
        print(f"[+] Found record in Supabase (id: {latest.get('id')})")
        print(f"   User Msg: {latest.get('user_message')[:30]}...")
        print(f"   AI Resp:  {latest.get('assistant_response')[:30]}...")
    else:
        print("[-] Failed to find conversation record in Supabase.")

if __name__ == "__main__":
    asyncio.run(verify_astra_knowledge())
