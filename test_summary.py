import asyncio
import httpx
import json
import time
from datetime import datetime

# We will test both the remote Cloudflare URL and the internal API URL
URLS = [
    "https://metal-rotary-nano-heavily.trycloudflare.com",
    "https://api.ayureze.in"
]

ENDPOINTS = [
    {"path": "/health", "method": "GET"},
    {"path": "/api/v1/brain/health", "method": "GET"},
    {"path": "/api/v1/astra/health", "method": "GET"},
    {"path": "/api/v1/brain/chat", "method": "POST", "payload": {"query": "Tell me about Ashwagandha"}},
    {"path": "/v1/chat", "method": "POST", "payload": {"query": "Test chat"}},
    {"path": "/api/v1/brain/autopilot", "method": "POST", "payload": {"query": "Book an appointment"}},
    {"path": "/v1/autopilot", "method": "POST", "payload": {"query": "Find doctor"}},
    {"path": "/api/v1/brain/fill", "method": "POST", "payload": {"text": "Subhash is 30 years old", "schema_definition": "{}"}},
    {"path": "/v1/fill", "method": "POST", "payload": {"text": "Test extraction", "schema_definition": "{}"}},
    {"path": "/api/v1/brain/doctor-summary", "method": "POST", "payload": {"notes": "Patient has headache"}},
    {"path": "/v1/doctor", "method": "POST", "payload": {"notes": "Summary test"}},
]

async def test_all():
    print(f"Starting Comprehensive AI Brain Audit at {datetime.now().isoformat()}")
    results = []
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for base in URLS:
            print(f"\n--- Testing Base: {base} ---")
            for ep in ENDPOINTS:
                path = ep["path"]
                method = ep["method"]
                payload = ep.get("payload")
                url = f"{base}{path}"
                
                print(f"Testing {method} {url:60} ...", end=" ", flush=True)
                start = time.time()
                try:
                    if method == "GET":
                        resp = await client.get(url)
                    else:
                        resp = await client.post(url, json=payload)
                    
                    duration = time.time() - start
                    status = resp.status_code
                    success = 200 <= status < 300
                    print(f"{status} ({duration:.2f}s)")
                    
                    results.append({
                        "base": base,
                        "path": path,
                        "method": method,
                        "status": status,
                        "duration": duration,
                        "success": success,
                        "response": resp.text[:200]
                    })
                except Exception as e:
                    duration = time.time() - start
                    print(f"ERROR: {type(e).__name__} ({duration:.2f}s)")
                    results.append({
                        "base": base,
                        "path": path,
                        "method": method,
                        "status": "ERROR",
                        "duration": duration,
                        "success": False,
                        "error": str(e)
                    })

    # Generate Report
    report_file = "DETAILED_AI_BRAIN_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Detailed Astra AI Brain Connectivity Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for base in URLS:
            f.write(f"## Target: {base}\n")
            f.write("| Endpoint | Method | Status | Latency | Result |\n")
            f.write("|----------|--------|--------|---------|--------|\n")
            base_results = [r for r in results if r["base"] == base]
            for r in base_results:
                icon = "✅ PASS" if r["success"] else "❌ FAIL"
                f.write(f"| `{r['path']}` | {r['method']} | {r['status']} | {r['duration']:.2f}s | {icon} |\n")
            f.write("\n")
            
    print(f"\nAudit complete. Report saved to {report_file}")

if __name__ == "__main__":
    asyncio.run(test_all())
