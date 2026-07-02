import requests
import json

def get_openapi_token():
    url = "https://astra.ayureze.in/openapi.json"
    try:
        resp = requests.get(url)
        data = resp.json()
        path = "/api/v1/video/token"
        if path in data["paths"]:
            print(json.dumps(data["paths"][path], indent=2))
        else:
            # Maybe I misread the output? Let's print all /video/ paths
            for p in data["paths"]:
                if "video" in p:
                    print(p)
                    print(json.dumps(data["paths"][p], indent=2))
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    get_openapi_token()
