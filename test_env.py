import httpx
print("SUCCESS: httpx imported")
import asyncio
print("SUCCESS: asyncio imported")
import os
import sys
print(f"INFO: Current directory: {os.getcwd()}")
print(f"INFO: Python version: {sys.version}")

async def test():
    async with httpx.AsyncClient() as client:
        print("SUCCESS: httpx client created")
        try:
            resp = await client.get("https://api.ayureze.in/health")
            print(f"SUCCESS: Response from api.ayureze.in/health: {resp.status_code}")
            print(f"Response body: {resp.text}")
        except Exception as e:
            print(f"ERROR: Error connecting to api.ayureze.in: {e}")

if __name__ == "__main__":
    asyncio.run(test())
