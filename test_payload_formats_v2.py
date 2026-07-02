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
    test_endpoint("/v1/detect_emotion", "I am happy", "Scalar String")
    test_endpoint("/v1/adjust_tone", {"text": "What is this?", "target_tone": "warm"}, "Tone Map")
    test_endpoint("/v1/generate_wellness", {"topic": "Sleep", "duration": "5m"}, "Wellness Map")
