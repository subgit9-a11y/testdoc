import requests
import json
import time

def test_api_ayureze():
    base_url = "https://api.ayureze.in"
    print(f"--- Testing {base_url} ---")

    # 1. Health Check
    try:
        print(f"GET {base_url}/health")
        resp = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Ask (from integration guide)
    payload_ask = {
        "query": "Astra: hi",
        "language": "en",
        "stream": False
    }
    try:
        print(f"\nPOST {base_url}/ask")
        resp = requests.post(f"{base_url}/ask", json=payload_ask, timeout=60)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. v1/chat (from astra_brain_client.py)
    payload_chat = {
        "q": "Explain the benefits of Ashwagandha"
    }
    try:
        print(f"\nPOST {base_url}/v1/chat")
        resp = requests.post(f"{base_url}/v1/chat", json=payload_chat, timeout=60)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 4. v1/autopilot
    try:
        print(f"\nPOST {base_url}/v1/autopilot")
        resp = requests.post(f"{base_url}/v1/autopilot", json={"q": "I want to book an appointment"}, timeout=60)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_ayureze()
