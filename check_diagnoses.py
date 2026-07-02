import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure local 'app' is in path
sys.path.append(os.getcwd())
load_dotenv()

from app.astra.pipeline import AstraPipeline

async def check_diagnoses():
    print("\n--- [DIAGNOSIS AUDIT] ---")
    pipeline = AstraPipeline()
    user_id = "diagnosis_audit_test"
    
    scenarios = [
        "I have chronic burning sensation in my chest and sour belching after meals.",
        "My knee joints are stiff and painful, especially in the morning and cold weather.",
        "I have chronic constipation and feel bloated all the time."
    ]
    
    for query in scenarios:
        print(f"\nQUERY: {query}")
        response = await pipeline.process_query(user_id=user_id, message=query, history=[])
        print(f"AI RESPONSE SYNOPSIS: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(check_diagnoses())
