import asyncio
import httpx
import json
import time
from datetime import datetime

# CONFIGURATION
BASE_URL = "http://localhost:8001"
REPORT_FILE = "ai_audit_report.json"

# ENDPOINTS TO TEST (Including aliases from main_agent.py)
ENDPOINTS = [
    # Health & System
    {"path": "/", "method": "GET"},
    {"path": "/health", "method": "GET"},
    {"path": "/api/v1/health", "method": "GET"},
    {"path": "/api/v1/astra/health", "method": "GET"},
    {"path": "/api/v1/brain/health", "method": "GET"},
    {"path": "/health/live", "method": "GET"},
    {"path": "/health/ready", "method": "GET"},
    
    # Chat & RAG (All versions)
    {"path": "/v1/chat", "method": "POST", "body": {"query": "Tell me about Ashwagandha", "language": "en"}},
    {"path": "/api/v1/brain/chat", "method": "POST", "body": {"query": "Test chat", "language": "en"}},
    {"path": "/api/v1/astra/chat", "method": "POST", "body": {"query": "Test chat", "language": "en"}},
    {"path": "/api/v1/chat/completions", "method": "POST", "body": {"query": "Test chat", "language": "en"}},
    {"path": "/ask", "method": "POST", "body": {"query": "What is Pitta?", "language": "en"}},
    {"path": "/api/v1/chat/message", "method": "POST", "body": {"query": "Hi", "language": "en"}},
    
    # Autopilot & Intent
    {"path": "/v1/autopilot", "method": "POST", "body": {"query": "I want to book an appointment"}},
    {"path": "/api/v1/brain/autopilot", "method": "POST", "body": {"query": "Book a doctor"}},
    {"path": "/api/v1/autopilot/debug/trigger/test_patient", "method": "POST", "body": {"query": "EVALUATE"}},
    {"path": "/v1/get_intent", "method": "POST", "body": {"query": "Check my pulse"}},

    # Astra Fill & Extraction
    {"path": "/v1/fill", "method": "POST", "body": {"text": "Patient is 30 years old", "schema_definition": "{}"}},
    {"path": "/api/v1/brain/fill", "method": "POST", "body": {"text": "Extraction test", "schema_definition": "{}"}},
    {"path": "/api/v1/astra-fill/process-text", "method": "POST", "body": {"text": "Process this", "schema_definition": "{}"}},

    # Clinical Services
    {"path": "/v1/extract_schedule", "method": "POST", "body": {"prescription_text": "One tab in morning"}},
    {"path": "/api/v1/brain/extract-schedule", "method": "POST", "body": {"prescription_text": "One tab in morning"}},
    {"path": "/v1/schedule", "method": "POST", "body": {"prescription_text": "One tab in morning"}},
    {"path": "/v1/doctor_summary", "method": "POST", "body": {"notes": "Patient has fever"}},
    {"path": "/api/v1/brain/doctor-summary", "method": "POST", "body": {"notes": "Patient has fever"}},
    {"path": "/v1/doctor", "method": "POST", "body": {"notes": "Summary test"}},

    # Safety & Emotions
    {"path": "/v1/analyze_safety", "method": "POST", "body": {"text": "Is this safe?", "analysis_type": "safety"}},
    {"path": "/api/v1/brain/analyze-safety", "method": "POST", "body": {"text": "Is this safe?", "analysis_type": "safety"}},
    {"path": "/v1/detect_emotion", "method": "POST", "body": {"text": "I am feeling happy", "analysis_type": "emotion"}},
    {"path": "/api/v1/brain/detect-emotion", "method": "POST", "body": {"text": "I am feeling happy", "analysis_type": "emotion"}},

    # Shop Assist
    {"path": "/v1/shop_assist", "method": "POST", "body": {"query": "Suggest a product"}},
    {"path": "/api/v1/brain/shop-assist", "method": "POST", "body": {"query": "Suggest a product"}},
    {"path": "/v1/shop", "method": "POST", "body": {"query": "Suggest a product"}},

    # Wellness & Profiles
    {"path": "/v1/generate_wellness", "method": "POST", "body": {"topic": "Yoga", "duration": "5 min"}},
    {"path": "/api/v1/brain/generate-wellness", "method": "POST", "body": {"topic": "Yoga", "duration": "5 min"}},
    {"path": "/v1/profile_analysis", "method": "POST", "body": {"profile_data_a": "A", "task": "match"}},
    {"path": "/api/v1/brain/profile-analysis", "method": "POST", "body": {"profile_data_a": "A", "task": "match"}},
    {"path": "/v1/adjust_tone", "method": "POST", "body": {"text": "Hi", "target_tone": "polite"}},
    {"path": "/api/v1/brain/adjust-tone", "method": "POST", "body": {"text": "Hi", "target_tone": "polite"}},

    # Metadata
    {"path": "/api/v1/brain/endpoints", "method": "GET"},
]

async def run_audit():
    results = []
    success_count = 0
    fail_count = 0
    
    print(f"STARTING COMPREHENSIVE AI AUDIT: {BASE_URL}...")
    
    # Sort endpoints to ensure health checks run first
    sorted_endpoints = sorted(ENDPOINTS, key=lambda x: x["method"] != "GET")
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for ep in sorted_endpoints:
            path = ep["path"]
            method = ep["method"]
            body = ep.get("body", {})
            
            start_time = time.time()
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                else:
                    response = await client.post(f"{BASE_URL}{path}", json=body)
                
                latency = round((time.time() - start_time) * 1000, 2)
                
                status_code = response.status_code
                is_ok = 200 <= status_code < 300
                
                if is_ok:
                    success_count += 1
                else:
                    fail_count += 1
                
                results.append({
                    "path": path,
                    "method": method,
                    "status": "PASS" if is_ok else "FAIL",
                    "status_code": status_code,
                    "latency_ms": latency,
                    "response_summary": str(response.json())[:100] if status_code == 200 else response.text[:100]
                })
                
                status_label = "[PASS]" if is_ok else "[FAIL]"
                print(f"{status_label} {method:4} {path:40} - {status_code} ({latency}ms)")
                
            except Exception as e:
                fail_count += 1
                error_msg = str(e)
                print(f"[ERROR] {method:4} {path:40} - ERROR: {error_msg}")
                results.append({
                    "path": path,
                    "method": method,
                    "status": "ERROR",
                    "error": error_msg
                })

    # Summary Report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tested": len(sorted_endpoints),
            "success": success_count,
            "failure": fail_count,
            "uptime_pct": round((success_count / len(sorted_endpoints)) * 100, 2) if sorted_endpoints else 0
        },
        "details": results
    }
    
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)
    
    print("\n" + "=" * 60)
    print(f"AUDIT COMPLETE")
    print(f"Total Tested: {len(sorted_endpoints)}")
    print(f"Passed: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Detailed JSON Report: {REPORT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_audit())
