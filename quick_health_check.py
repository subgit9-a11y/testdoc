import requests
import time

URLS = [
    "https://api.ayureze.in/health",
    "https://metal-rotary-nano-heavily.trycloudflare.com/api/v1/brain/health",
    "https://metal-rotary-nano-heavily.trycloudflare.com/health",
    "http://localhost:8000/health",
    "http://localhost:8001/health"
]

def check():
    for url in URLS:
        print(f"Checking {url}...")
        try:
            start = time.time()
            resp = requests.get(url, timeout=5)
            duration = time.time() - start
            print(f"  Result: {resp.status_code} ({duration:.2f}s)")
        except Exception as e:
            print(f"  Result: ERROR: {e}")

if __name__ == "__main__":
    check()
