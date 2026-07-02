import httpx
import os
import asyncio
from dotenv import load_dotenv

async def test_wa():
    load_dotenv()
    url = os.getenv('CUSTOM_WA_API_BASE_URL')
    token = os.getenv('CUSTOM_WA_BEARER_TOKEN')
    vendor = os.getenv('CUSTOM_WA_VENDOR_UID')
    
    print(f"Testing Custom WhatsApp Gateway: {url}")
    print(f"Vendor: {vendor}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health on the root or /api/health
            r = await client.get(f"{url}/whatsapp/health", timeout=10.0)
            print(f"Health check status: {r.status_code}")
            print(f"Health JSON: {r.text[:200]}")
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_wa())
