import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Ensure local 'app' is in path
sys.path.append(os.getcwd())
load_dotenv()

from app.astra.pipeline import AstraPipeline
from app.database import db_manager

# Set logging to see details
logging.basicConfig(level=logging.INFO)

async def run_headache_flow():
    print("\n--- [FLOW] Patient Query: Severe One-Sided Headache ---")
    
    # 1. Setup Pipeline
    pipeline = AstraPipeline()
    user_id = "patient_headache_001"
    query = "i had severe one sided headache what to do"
    
    print(f"\nQUERY: {query}")
    
    # 2. Process via AI Pipeline
    # This will trigger: Safety -> Emotion -> Chat -> Supabase Storage
    response = await pipeline.process_query(
        user_id=user_id,
        message=query,
        history=[]
    )
    
    print(f"\nASTRA RESPONSE: \n{response}")
    
    # 3. Verify Supabase Storage
    print("\nCHECKING Supabase record...")
    await asyncio.sleep(2) # Wait for storage
    
    history = await db_manager.get_user_chat_history(user_id=user_id, limit=1)
    
    if history:
        latest = history[0]
        print(f"[+] Record found in Supabase (id: {latest.get('id')})")
        print(f"   Stored User Msg: {latest.get('user_message')}")
        print(f"   Stored AI Resp:  {latest.get('assistant_response')[:50]}...")
    else:
        print("[-] Conversation record NOT found in Supabase.")

if __name__ == "__main__":
    asyncio.run(run_headache_flow())
