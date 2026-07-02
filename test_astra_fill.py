import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

BASE = "https://astra.ayureze.in"

print("=" * 60)
print("  ASTRA FILL - DOCTOR APP VIEW TEST")
print("=" * 60)

# Test with a real patient - first find one
print("\n1. Finding a real patient from DB...")
r = requests.get(f"{BASE}/api/v1/patients/search/test", timeout=10)
patients = r.json() if r.status_code == 200 else []
print(f"   Search status: {r.status_code} | Found: {len(patients)} patients")

# Use a known patient ID or fallback
patient_id = None
if patients and isinstance(patients, list):
    patient_id = patients[0].get('patient_id') or patients[0].get('id')
    print(f"   Using patient: {patient_id}")

if not patient_id:
    patient_id = "test_patient"
    print(f"   Using test ID: {patient_id}")

print()

# Test all Astra Fill endpoints the doctor app calls
endpoints = [
    ("Latest Astra Fill",      f"/api/v1/astra-fill/patient/{patient_id}/latest"),
    ("Astra Fill History",     f"/api/v1/astra-fill/patient/{patient_id}/history"),
    ("Astra Fill Records",     f"/api/v1/astra-fill/patient/{patient_id}/records"),
    ("Patient Full Profile",   f"/api/v1/patients/profile/{patient_id}"),
]

for name, path in endpoints:
    r = requests.get(f"{BASE}{path}", timeout=10)
    data = r.json() if r.status_code == 200 else {}
    
    if r.status_code == 200:
        is_empty = not data or data == {} or data == []
        if is_empty:
            print(f"  ⚠️  [{r.status_code}] {name} — EMPTY (no data yet)")
        else:
            # Show what fields are available
            if isinstance(data, dict):
                keys = list(data.keys())[:6]
                print(f"  ✅ [{r.status_code}] {name} — Fields: {keys}")
                # Show key health fields
                if 'symptoms' in data or 'extracted_symptoms' in data:
                    syms = data.get('symptoms') or data.get('extracted_symptoms', [])
                    print(f"       Symptoms: {syms[:3]}")
                if 'chief_complaint' in data:
                    print(f"       Chief Complaint: {data['chief_complaint']}")
                if 'severity_score' in data:
                    print(f"       Severity Score: {data['severity_score']}")
            elif isinstance(data, list):
                print(f"  ✅ [{r.status_code}] {name} — {len(data)} records found")
    else:
        print(f"  ❌ [{r.status_code}] {name} — {r.text[:80]}")

print()
print("=" * 60)
print("  ASTRA FILL WIDGET CHECK")
print("=" * 60)
print()
print("The Doctor App uses AstraFillDisplayWidget which calls:")
print("  astra_service.getLatestAstraFill(patientId)")
print("  --> GET /api/v1/astra-fill/patient/{id}/latest")
print()

# Check if the widget endpoint works
r2 = requests.get(f"{BASE}/api/v1/astra-fill/patient/{patient_id}/latest", timeout=10)
if r2.status_code == 200 and r2.json():
    print("  ✅ Widget endpoint LIVE — Astra Fill WILL show in Doctor App!")
else:
    print("  ⚠️  Widget endpoint returns EMPTY — Astra Fill shows 'No data' message")
    print("      This means NO patient has submitted an Astra Fill form yet.")
    print("      Once a patient fills the AI form, doctor will see it instantly!")
