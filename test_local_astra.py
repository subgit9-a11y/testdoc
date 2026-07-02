import requests
import json
import time

def test_local_astra():
    base_url = "http://localhost:5000"
    print(f"--- Testing Local Astra at {base_url} ---")

    # 1. Health
    try:
        print(f"GET {base_url}/health")
        resp = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. API v1 Health
    try:
        print(f"\nGET {base_url}/api/v1/health")
        resp = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_local_astra()
