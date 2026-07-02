import requests
import json

base_url = "https://api.ayureze.in"

def test_endpoint(path, payload, label):
    print(f"--- Testing {path} with {label} ---")
    try:
        resp = requests.post(f"{base_url}{path}", json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test shop_assist
    test_endpoint("/v1/shop_assist", "Triphala", "Scalar String")
    test_endpoint("/v1/shop_assist", {"q": "Triphala"}, "Object with q")
    
    # Test extract_schedule
    test_endpoint("/v1/extract_schedule", "Take 1 pill after dinner", "Scalar String")
    
    # Test analyze_safety
    test_endpoint("/v1/analyze_safety", "Is this safe?", "Scalar String")
