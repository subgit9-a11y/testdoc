import requests

BASE_URL = "https://astra.ayureze.in"
HEADERS = {
    "X-API-Key": "astra-secret-2026",
    "Authorization": "Bearer dummy_token_for_test",
    "Content-Type": "application/json"
}

def check_500_error():
    print("Checking AI Brain health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/brain/health", headers=HEADERS)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nChecking failing endpoint: GET /api/v1/api/doctors/test-123/dashboard-stats")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/api/doctors/test-123/dashboard-stats", headers=HEADERS)
        print(f"Status: {r.status_code}")
        print(f"Response (first 1000 chars): {r.text[:1000]}")
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nChecking failing endpoint: GET /api/companion/case/test-123")
    try:
        r = requests.get(f"{BASE_URL}/api/companion/case/test-123", headers=HEADERS)
        print(f"Status: {r.status_code}")
        print(f"Response (first 1000 chars): {r.text[:1000]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_500_error()
