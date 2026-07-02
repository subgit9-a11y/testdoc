import requests

def test_agora():
    url = "https://astra.ayureze.in/api/v1/video/generate-token"
    # Note: Requires a logged in user with valid token, or we might get 401. 
    # Let's try sending it to see if we get a token or a 401 Unauthorized.
    # If 401, it means the endpoint is secured and active.
    # If it works, great.
    
    payload = {
        "to_id": "123",
        "uid": 0
    }
    
    try:
        resp = requests.post(url, json=payload, headers={"Authorization": "Bearer TEST"})
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_agora()
