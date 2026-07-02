import httpx
import asyncio
import json
import traceback

async def diagnostic():
    url = "https://api.ayureze.in"
    endpoints = [
        # (endpoint, sample_payload)
        ("/v1/doctor_summary", "Herbs for sleep"),
        ("/v1/generate_wellness", {"topic": "Meditation", "duration": "5 mins"}),
        ("/v1/adjust_tone", {"text": "How to take it?", "target_tone": "polite"}),
        ("/v1/detect_emotion", "I am happy")
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for ep, payload in endpoints:
            print(f"Testing {ep}...")
            try:
                # Use json= payload if it's a dict, otherwise it's a scalar string
                res = await client.post(f"{url}{ep}", json=payload)
                
                print(f"   Status: {res.status_code}")
                # Use repr to see control characters if any
                print(f"   Body: {repr(res.text[:200])}")
            except Exception as e:
                print(f"   Exception on {ep}: {repr(e)}")
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnostic())
