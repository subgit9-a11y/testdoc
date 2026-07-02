import requests
import json
import time

def test_api_ayureze():
    base_url = "https://api.ayureze.in"
    print(f"--- Testing {base_url} ---")

    # 1. /api/v1/brain/chat (from api_openapi.json)
    payload_brain_chat = {
        "query": "Explain the benefits of Ashwagandha",
        "language": "en"
    }
    try:
        print(f"\nPOST {base_url}/api/v1/brain/chat")
        resp = requests.post(f"{base_url}/api/v1/brain/chat", json=payload_brain_chat, timeout=60)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_ayureze()
