import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

BASE = "https://astra.ayureze.in"
DOCTOR_ID = "DOC-20"

print("=" * 60)
print("  PRESCRIPTION SECTION - DOCTOR APP FULL TEST")
print("=" * 60)

results = []

def test(name, method, path, data=None):
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=12)
        else:
            r = requests.post(url, json=data, timeout=12)
        ok = r.status_code in [200, 201]
        results.append({"name": name, "status": r.status_code, "ok": ok, "data": r.json() if ok else {}})
        symbol = "✅" if ok else "❌"
        print(f"  {symbol} [{r.status_code}] {name}")
        if not ok:
            print(f"       └─ {r.text[:120]}")
        return r.json() if ok else {}
    except Exception as e:
        results.append({"name": name, "status": "ERR", "ok": False, "data": {}})
        print(f"  ❌ [ERR] {name} → {str(e)[:80]}")
        return {}

# ── 1. Patient Prescriptions ──
print("\n── 1. FETCH PRESCRIPTIONS ──")
test("Get Patient Prescriptions",     "GET", "/api/v1/api/prescriptions/patient/PAT-001")
test("Get Patient Prescriptions (v2)","GET", "/api/v1/prescriptions/patient/PAT-001")

# ── 2. Create Prescription ──
print("\n── 2. CREATE PRESCRIPTION ──")
rx_payload = {
    "prescription_id": "rx_test_001",
    "doctor": {
        "name": "Dr. Test Subash",
        "regn_no": "DOC-20",
        "qualification": "BAMS",
        "hospital": "Ayureze Clinic"
    },
    "patient": {
        "patient_id": "PAT-TEST",
        "name": "Test Patient",
        "age": 30,
        "gender": "Male",
        "phone": "9999999999"
    },
    "diagnosis": "General wellness checkup",
    "prescriptions": [
        {
            "medicine": "Abhayarishtam",
            "dose": "15ml",
            "schedule": "Twice daily",
            "timing": "After food",
            "quantity": 1,
            "duration": "7 days"
        }
    ],
    "doctor_notes": "Stay hydrated"
}
# Test validate only (safe, no actual order)
test("Validate Prescription",         "POST", "/api/v1/shopify/validate-prescription", rx_payload)

# ── 3. Catchy Prescription (AI) ──
print("\n── 3. AI CATCHY PRESCRIPTION ──")
catchy_payload = {
    "doctor_name": "Dr. Test Subash",
    "patient_name": "Test Patient",
    "diagnosis": "Headache and fever",
    "medicines": ["Abhayarishtam", "Vivadona"]
}
test("Auto-Generate Catchy Prescription", "POST", "/api/v1/prescriptions/auto-generate-catchy", catchy_payload)

# ── 4. Prescription Workflow ──
print("\n── 4. PRESCRIPTION WORKFLOW ──")
test("Check Workflow Status",         "GET", "/api/v1/prescription-workflow/status/rx_test_001")

# ── 5. Shopify Draft Order ──
print("\n── 5. SHOPIFY MEDICINE AVAILABILITY ──")
test("Search Medicine (Abhayarishtam)","GET", "/api/v1/shopify/products/search/Abhayarishtam")
test("Get Draft Order",               "GET", "/api/v1/shopify/draft-order/999999")

# ── 6. AI Brain Prescription Help ──
print("\n── 6. AI BRAIN PRESCRIPTION ASSIST ──")
test("Generate Doctor Summary",       "POST", "/api/v1/brain/doctor_summary",
     {"notes": "Patient has fever 102F and headache for 2 days"})
test("Analyze Medication Safety",     "POST", "/api/v1/brain/analyze_safety",
     {"text": "Abhayarishtam 15ml twice daily"})
test("Extract Schedule",              "POST", "/api/v1/brain/extract_schedule",
     {"prescription_text": "Abhayarishtam 15ml twice daily after food for 7 days"})

# Summary
print()
print("=" * 60)
passed = sum(1 for r in results if r["ok"])
failed = len(results) - passed
print(f"  RESULT: {passed}/{len(results)} PASSED  |  {failed} FAILED")
print("=" * 60)

if failed > 0:
    print("\n  FAILING ENDPOINTS:")
    for r in results:
        if not r["ok"]:
            print(f"   • {r['name']} [{r['status']}]")
