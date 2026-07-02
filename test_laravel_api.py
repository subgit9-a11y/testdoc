import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_laravel_api():
    url = os.getenv("LARAVEL_BACKEND_URL", "https://ayureze.org/api")
    key = os.getenv("LARAVEL_API_KEY", "")
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json"
    }
    
    print(f"Testing Laravel API at {url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Try a common endpoint or just the base
            endpoints = ["doctors", "api/doctors", "get-doctors"]
            for ep in endpoints:
                full_url = f"{url}/{ep}" if not url.endswith("/") else f"{url}{ep}"
                print(f"Checking {full_url}...")
                resp = await client.get(full_url, headers=headers, timeout=5)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Data: {resp.json()[:1] if isinstance(resp.json(), list) else 'Not a list'}")
                    break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_laravel_api())
