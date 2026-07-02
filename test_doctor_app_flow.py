import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json

BASE = "https://astra.ayureze.in"
DOCTOR_ID = "DOC-20"  # TEST SUBASH

results = []

def test(name, method, path, data=None, params=None):
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, params=params, timeout=10)
        else:
            r = requests.post(url, json=data, timeout=10)
        
        ok = r.status_code in [200, 201]
        results.append({"name": name, "status": r.status_code, "ok": ok})
        symbol = "✅" if ok else "❌"
        print(f"{symbol} [{r.status_code}] {name}")
        if not ok:
            print(f"   └─ {r.text[:120]}")
    except Exception as e:
        results.append({"name": name, "status": "TIMEOUT", "ok": False})
        print(f"❌ [TIMEOUT] {name} → {str(e)[:80]}")

print("=" * 60)
print("  DOCTOR APP → ASTRA AI CONNECTION FLOW TEST")
print(f"  Backend: {BASE}")
print("=" * 60)

print("\n── 1. HEALTH CHECKS ──")
test("Backend Health",              "GET", "/health")
test("API v1 Health",               "GET", "/api/v1/health")

print("\n── 2. DOCTOR IDENTITY ──")
test("Get Doctor Profile (v1)",     "GET", f"/api/v1/api/doctors/{DOCTOR_ID}")
test("Get Doctor Dashboard Stats",  "GET", f"/api/v1/api/doctors/{DOCTOR_ID}/dashboard-stats")

print("\n── 3. PATIENT MANAGEMENT ──")
test("Search Patients",             "GET", "/api/v1/patients/search/test")
test("Get Patient Profile",         "GET", "/api/v1/patients/profile/PAT-001")

print("\n── 4. ASTRA AI BRAIN ──")
test("Brain Chat",                  "POST", "/api/v1/brain/chat",
     data={"message": "hello", "user_id": DOCTOR_ID, "user_metadata": {"role": "doctor"}})
test("Brain Health",                "GET", "/api/v1/brain/health")

print("\n── 5. ASTRA FILL (Patient Intake) ──")
test("Get Latest Astra Fill",       "GET", "/api/v1/astra-fill/patient/PAT-001/latest")
test("Get Astra Fill History",      "GET", "/api/v1/astra-fill/patient/PAT-001/history")

print("\n── 6. PRESCRIPTIONS ──")
test("Get Patient Prescriptions",   "GET", "/api/v1/api/prescriptions/patient/PAT-001")

print("\n── 7. SHOPIFY / MEDICINES ──")
test("Available Medicines",         "GET", "/api/v1/shopify/products/available")
test("Search Medicine",             "GET", "/api/v1/shopify/products/search/ashwagandha")

print("\n── 8. DOCUMENTS ──")
test("List Patient Documents",      "GET", "/api/v1/documents/patient/PAT-001")

print("\n── 9. NOTIFICATIONS ──")
test("Notification Status",         "GET", "/api/v1/notifications/service-status")

print("\n── 10. TRANSLATION ──")
test("Supported Languages",         "GET", "/api/v1/api/translate/languages")

print("\n" + "=" * 60)
passed = sum(1 for r in results if r["ok"])
failed = len(results) - passed
print(f"  RESULT: {passed}/{len(results)} PASSED  |  {failed} FAILED")
print("=" * 60)
if failed > 0:
    print("\n❌ FAILING ENDPOINTS:")
    for r in results:
        if not r["ok"]:
            print(f"   • {r['name']} [{r['status']}]")
