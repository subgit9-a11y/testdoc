import requests
import json

base_url = "https://astra.ayureze.in"

print("Logging in as Dr. Subashdr (Legacy ID: DOC-11)...")

paths = [
    "/api/doctors/DOC-11",
    "/api/v1/api/doctors/DOC-11",
    "/doctors/DOC-11"
]

for path in paths:
    print(f"\\nTesting: {base_url}{path}")
    res = requests.get(f"{base_url}{path}")
    print("Status Code:", res.status_code)
    try:
        print("Response:", json.dumps(res.json(), indent=2))
    except:
        print("Response:", res.text)
