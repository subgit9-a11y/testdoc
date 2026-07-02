import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    try:
        raise HTTPException(status_code=404, detail="Case not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

client = TestClient(app)

if __name__ == "__main__":
    response = client.get("/test")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
