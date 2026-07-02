import requests
import json

base_url = "https://api.ayureze.in"

def test_fill():
    path = "/v1/fill"
    payload = {"text": "I have a cold for 2 days", "schema_def": '{"symptoms": "list", "duration": "string"}'}
    print(f"--- Testing {path} ---")
    try:
        resp = requests.post(f"{base_url}{path}", json=payload, timeout=20)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fill()
