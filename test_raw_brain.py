import asyncio
import httpx
import json

async def diagnostic():
    url = "https://api.ayureze.in/v1"
    headers = {"Content-Type": "application/json"}
    
    print("AI Brain Raw Output Diagnosis:")
    print("="*60)
    
    # 1. Chat
    print("\n1. /chat")
    try:
        resp = await httpx.AsyncClient().post(f"{url}/chat", json={"q": "Hi"}, timeout=30.0)
        print(f"   Status: {resp.status_code}")
        print(f"   Body: {resp.text}")
    except Exception as e: print(f"   Error: {e}")

    # 2. Fill
    print("\n2. /fill")
    try:
        resp = await httpx.AsyncClient().post(f"{url}/fill", json={"text": "I am 30", "schema_def": "age:int"}, timeout=30.0)
        print(f"   Status: {resp.status_code}")
        print(f"   Body: {resp.text}")
    except Exception as e: print(f"   Error: {e}")

    # 3. Autopilot
    print("\n3. /autopilot")
    try:
        resp = await httpx.AsyncClient().post(f"{url}/autopilot", json={"q": "Book doctor"}, timeout=30.0)
        print(f"   Status: {resp.status_code}")
        print(f"   Body: {resp.text}")
    except Exception as e: print(f"   Error: {e}")

    # 4. Extract Schedule
    print("\n4. /extract_schedule")
    try:
        resp = await httpx.AsyncClient().post(f"{url}/extract_schedule", json="Triphala at night", timeout=30.0)
        print(f"   Status: {resp.status_code}")
        print(f"   Body: {resp.text}")
    except Exception as e: print(f"   Error: {e}")

    # 5. Shop Assist
    print("\n5. /shop_assist")
    try:
        resp = await httpx.AsyncClient().post(f"{url}/shop_assist", json="Herbs for cold", timeout=30.0)
        print(f"   Status: {resp.status_code}")
        print(f"   Body: {resp.text}")
    except Exception as e: print(f"   Error: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(diagnostic())
