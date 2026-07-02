"""
Investigate the 5 timed-out endpoints from the full patient flow test.
Run each individually with a 60-second timeout and detailed error reporting.
"""
import requests
import json
import sys
import time
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://astra.ayureze.in"
HEADERS = {
    "X-API-Key": "astra-secret-2026",
    "Content-Type": "application/json"
}
TIMEOUT = 60  # 60 seconds

def test_endpoint(name, method, url, **kwargs):
    print(f"\n{'='*60}")
    print(f"  Testing: {name}")
    print(f"  {method} {url}")
    print(f"  Timeout: {TIMEOUT}s")
    start = time.time()
    try:
        kwargs["headers"] = HEADERS
        kwargs["timeout"] = TIMEOUT
        if method == "POST":
            r = requests.post(url, **kwargs)
        elif method == "GET":
            r = requests.get(url, **kwargs)
        elif method == "PUT":
            r = requests.put(url, **kwargs)
        elapsed = time.time() - start
        print(f"  Status: {r.status_code} | Time: {elapsed:.1f}s")
        try:
            print(f"  Response: {json.dumps(r.json(), indent=2)[:600]}")
        except:
            print(f"  Response (raw): {r.text[:600]}")
        return r
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"  TIMEOUT after {elapsed:.1f}s")
        return None
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ERROR after {elapsed:.1f}s: {e}")
        return None


# FAIL 1: Search Nearby Doctors
test_endpoint(
    "Search Nearby Doctors",
    "GET",
    f"{BASE_URL}/api/v1/api/doctors/nearby/search",
    params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 50, "specialization": "Ayurveda"}
)

# FAIL 2: Save Prescription (Order Management)
test_endpoint(
    "Save Prescription (Orders)",
    "POST",
    f"{BASE_URL}/api/v1/orders/prescription/save",
    json={
        "patient_id": "test_patient_debug",
        "doctor_id": "dr_ayureze_001",
        "consultation_id": "test_case_001",
        "diagnosis": "Test diagnosis",
        "notes": "Test notes",
        "medicines": [
            {
                "medicine_name": "Ashwagandha Churna",
                "quantity": 1,
                "dose": "5g",
                "schedule": "twice_daily",
                "timing": "After meals",
                "duration": "30 days",
                "instructions": "Test"
            }
        ]
    }
)

# FAIL 3: Autopilot Consent
test_endpoint(
    "Autopilot Consent",
    "POST",
    f"{BASE_URL}/api/v1/autopilot/consent",
    json={"patient_id": "test_patient_debug", "consent_granted": True}
)

# FAIL 4: Create Medicine Reminder
test_endpoint(
    "Create Medicine Reminder",
    "POST",
    f"{BASE_URL}/api/v1/api/reminders/create",
    json={
        "patient_id": "test_patient_debug",
        "patient_name": "Test Patient",
        "patient_phone": "+919876543210",
        "medicine_name": "Ashwagandha Churna",
        "dosage": "5g",
        "frequency": "twice_daily",
        "times": ["09:00", "21:00"],
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "instructions": "Test",
        "enable_whatsapp": False
    }
)

# FAIL 5: Order History
test_endpoint(
    "Order History",
    "GET",
    f"{BASE_URL}/api/v1/orders/patient/test_patient_debug"
)

# Also check the Astra Fill extraction issue - the AI returned all "Not specified"
print("\n\n" + "="*60)
print("  BONUS: Checking Astra Fill extraction quality")
print("="*60)
test_endpoint(
    "Astra Fill (Text Intake)",
    "POST",
    f"{BASE_URL}/api/v1/astra-fill/process-text",
    data={
        "text": "I have chronic fatigue for 2 months. Poor digestion with bloating. Daily headaches in the evening. Tried paracetamol. Poor sleep quality.",
        "user_id": "test_patient_debug"
    },
    headers={"X-API-Key": "astra-secret-2026"}  # No Content-Type for form data
)

print("\n\nDone!")
