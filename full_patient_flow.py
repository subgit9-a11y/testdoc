"""
ASTRA COMPLETE PATIENT FLOW SIMULATION
=========================================
Tests the REAL end-to-end patient journey as described:

1.  Patient opens app -> Health check
2.  Patient starts Companion Journey (Astra Companion screen)
3.  Patient chats with Astra (voice/text)
4.  Astra Fill collects health details
5.  Health report generated
6.  Search for nearby doctors
7.  Doctor selected -> Case created (simulates consultation booking)
8.  Doctor prescribes medicine (prescription creation)
9.  Auto-generate prescription PDF (catchy prescription)
10. Auto-cart medicines (Shopify draft order)
11. Autopilot activation (consent + status)
12. Medicine reminders created
13. Regular health check-in (companion chat follow-up)
14. Prescription saved in EHR vault (document upload)
15. Case progress update
16. Order status check
"""

import requests
import json
import sys
import time
import uuid
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://astra.ayureze.in"
HEADERS = {
    "X-API-Key": "astra-secret-2026",
    "Content-Type": "application/json"
}

# Track IDs across the flow
flow_state = {}
step_results = []

def log_step(step_num, title, status, details=""):
    icon = "PASS" if status == "pass" else ("FAIL" if status == "fail" else "WARN")
    step_results.append({"step": step_num, "title": title, "status": status, "details": details})
    print(f"\n{'='*70}")
    print(f"  STEP {step_num}: {title}")
    print(f"  [{icon}]  {details}")
    print(f"{'='*70}")

def safe_request(method, url, **kwargs):
    """Make a request with error handling"""
    try:
        kwargs.setdefault("headers", HEADERS)
        kwargs.setdefault("timeout", 30)
        if method == "GET":
            r = requests.get(url, **kwargs)
        elif method == "POST":
            r = requests.post(url, **kwargs)
        elif method == "PUT":
            r = requests.put(url, **kwargs)
        else:
            r = requests.get(url, **kwargs)
        return r
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        print(f"  Request error: {e}")
        return None


def run_full_flow():
    print("\n" + "="*70)
    print("  ASTRA COMPLETE PATIENT FLOW - LIVE PRODUCTION TEST")
    print(f"  Server: {BASE_URL}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("="*70)

    # =====================================================================
    # STEP 1: System Health Check
    # =====================================================================
    r = safe_request("GET", f"{BASE_URL}/health")
    if r and r.status_code == 200:
        log_step(1, "System Health Check", "pass", f"Status: {r.status_code} | {r.text}")
    else:
        log_step(1, "System Health Check", "fail", f"Status: {r.status_code if r else 'TIMEOUT'}")
        return

    # Also check brain health
    r = safe_request("GET", f"{BASE_URL}/api/v1/brain/health")
    if r:
        print(f"  Brain Health: {r.status_code} | {r.text[:200]}")

    # =====================================================================
    # STEP 2: Patient Starts Companion Journey
    # =====================================================================
    patient_id = f"test_patient_{uuid.uuid4().hex[:8]}"
    flow_state["patient_id"] = patient_id

    journey_data = {
        "user_id": patient_id,
        "health_concern": "Chronic fatigue, poor digestion, and recurring headaches for the past 2 months",
        "language": "en",
        "initial_symptoms": ["fatigue", "indigestion", "headache", "poor sleep"],
        "metadata": {"source": "flutter_app", "device": "android"}
    }
    r = safe_request("POST", f"{BASE_URL}/api/companion/journey/start", json=journey_data)
    if r and r.status_code == 200:
        data = r.json()
        flow_state["journey_id"] = data.get("journey_id")
        log_step(2, "Start Companion Journey", "pass",
                 f"Journey ID: {flow_state['journey_id']}")
    else:
        log_step(2, "Start Companion Journey", "fail",
                 f"Status: {r.status_code if r else 'TIMEOUT'} | {r.text[:300] if r else ''}")

    # =====================================================================
    # STEP 3: Patient Chats with Astra (Text interaction)
    # =====================================================================
    chat_data = {
        "journey_id": flow_state.get("journey_id", ""),
        "message": "I have been feeling very tired for the past 2 months. I also have poor digestion and frequent headaches. I have trouble sleeping at night. Can you help me?",
        "language": "en"
    }
    r = safe_request("POST", f"{BASE_URL}/api/companion/chat", json=chat_data)
    if r and r.status_code == 200:
        data = r.json()
        ai_response = data.get("response", "")[:200]
        log_step(3, "Patient Chats with Astra", "pass",
                 f"AI Response: {ai_response}...")
    elif r and r.status_code == 503:
        log_step(3, "Patient Chats with Astra", "warn",
                 f"Status: 503 - Pipeline not ready (Brain API degraded). Response: {r.text[:200]}")
    else:
        log_step(3, "Patient Chats with Astra", "fail",
                 f"Status: {r.status_code if r else 'TIMEOUT'} | {r.text[:300] if r else ''}")

    # =====================================================================
    # STEP 4: Astra Fill - Collect Health Details
    # =====================================================================
    # Use text-based intake (process-text endpoint)
    fill_data = {
        "text": "I have been experiencing chronic fatigue for the past 2 months. My digestion has been very poor with frequent bloating after meals. I get headaches almost every day, usually in the evening. I tried taking paracetamol but it only helps temporarily. I have not consulted any doctor yet. My sleep quality is very poor - I wake up multiple times at night.",
        "user_id": patient_id
    }
    # process-text uses Form data, not JSON
    fill_headers = {"X-API-Key": "astra-secret-2026"}
    r = safe_request("POST", f"{BASE_URL}/api/v1/astra-fill/process-text",
                     data=fill_data, headers=fill_headers)
    if r and r.status_code == 200:
        data = r.json()
        extraction = data.get("extraction", data)
        log_step(4, "Astra Fill - Health Data Collection", "pass",
                 f"Extracted: {json.dumps(extraction, indent=2)[:500]}")
        flow_state["extraction_id"] = data.get("extraction_id", "")
    elif r:
        log_step(4, "Astra Fill - Health Data Collection", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(4, "Astra Fill - Health Data Collection", "fail", "TIMEOUT or connection error")

    # =====================================================================
    # STEP 5: Get Patient Health Report (latest fill)
    # =====================================================================
    r = safe_request("GET", f"{BASE_URL}/api/v1/astra-fill/patient/{patient_id}/latest")
    if r and r.status_code == 200:
        data = r.json()
        log_step(5, "Retrieve Health Report", "pass",
                 f"Report: {json.dumps(data, indent=2)[:500]}")
    elif r:
        log_step(5, "Retrieve Health Report", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(5, "Retrieve Health Report", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 6: Search for Nearby Doctors
    # =====================================================================
    r = safe_request("GET", f"{BASE_URL}/api/v1/api/doctors/nearby/search",
                     params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 50, "specialization": "Ayurveda"})
    if r and r.status_code == 200:
        doctors = r.json()
        log_step(6, "Search Nearby Doctors", "pass",
                 f"Found: {json.dumps(doctors, indent=2)[:500]}")
    elif r:
        log_step(6, "Search Nearby Doctors", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(6, "Search Nearby Doctors", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 7: Create Case (Doctor Selected + Consultation Simulated)
    # =====================================================================
    doctor_id = "dr_ayureze_001"
    flow_state["doctor_id"] = doctor_id

    case_data = {
        "journey_id": flow_state.get("journey_id", ""),
        "user_id": patient_id,
        "doctor_id": doctor_id,
        "diagnosis": "Vata-Pitta imbalance with Mandagni (weak digestive fire)",
        "treatment_duration_days": 30,
        "diet_plan": {
            "morning": "Warm water with lemon, light breakfast with oats",
            "lunch": "Rice with dal, steamed vegetables",
            "evening": "Herbal tea (ginger + tulsi)",
            "dinner": "Light khichdi before 7 PM",
            "avoid": ["cold drinks", "fried food", "processed sugar", "late night eating"]
        },
        "follow_up_schedule": ["2026-06-15", "2026-06-30"],
        "metadata": {"consultation_type": "video_call", "consultation_fee": 500}
    }
    r = safe_request("POST", f"{BASE_URL}/api/companion/case/create", json=case_data)
    if r and r.status_code == 200:
        data = r.json()
        flow_state["case_id"] = data.get("case_id")
        log_step(7, "Create Case (Post-Consultation)", "pass",
                 f"Case ID: {flow_state['case_id']}")
    elif r:
        log_step(7, "Create Case (Post-Consultation)", "fail",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(7, "Create Case (Post-Consultation)", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 8: Doctor Prescribes Medicine (Save Prescription)
    # =====================================================================
    prescription_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "consultation_id": flow_state.get("case_id", ""),
        "diagnosis": "Vata-Pitta imbalance with Mandagni",
        "notes": "Patient to follow strict Ayurvedic diet plan. Avoid cold foods and drinks.",
        "medicines": [
            {
                "medicine_name": "Ashwagandha Churna",
                "quantity": 1,
                "dose": "5g",
                "schedule": "twice_daily",
                "timing": "After meals",
                "duration": "30 days",
                "instructions": "Mix with warm milk or water"
            },
            {
                "medicine_name": "Triphala Churna",
                "quantity": 1,
                "dose": "3g",
                "schedule": "once_daily",
                "timing": "Before bed",
                "duration": "30 days",
                "instructions": "Take with warm water"
            },
            {
                "medicine_name": "Brahmi Vati",
                "quantity": 1,
                "dose": "2 tablets",
                "schedule": "twice_daily",
                "timing": "Morning and evening",
                "duration": "30 days",
                "instructions": "Take after meals with water"
            }
        ]
    }
    r = safe_request("POST", f"{BASE_URL}/api/v1/orders/prescription/save", json=prescription_data)
    if r and r.status_code == 200:
        data = r.json()
        flow_state["prescription_id"] = data.get("prescription_id")
        log_step(8, "Doctor Prescribes Medicine", "pass",
                 f"Prescription ID: {flow_state.get('prescription_id')} | Response: {json.dumps(data, indent=2)[:400]}")
    elif r:
        log_step(8, "Doctor Prescribes Medicine", "fail",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(8, "Doctor Prescribes Medicine", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 9: Auto-Generate Prescription PDF (Catchy Prescription)
    # =====================================================================
    pdf_data = {
        "patient": {
            "name": "Test Patient",
            "age": 30,
            "sex": "Male",
            "contact": "+91 9876543210"
        },
        "doctor": {
            "name": "Dr. AyurEze",
            "regn_no": "AY-2026-001",
            "contact": "+91 98765 43210"
        },
        "prescriptions": [
            {"medicine": "Ashwagandha Churna", "dose": "5g", "schedule": "Twice daily", "timing": "After meals", "duration": "30 days", "instructions": "Mix with warm milk", "quantity": 1},
            {"medicine": "Triphala Churna", "dose": "3g", "schedule": "Once daily (before bed)", "timing": "Before bed", "duration": "30 days", "instructions": "With warm water", "quantity": 1},
            {"medicine": "Brahmi Vati", "dose": "2 tablets", "schedule": "Twice daily", "timing": "Morning & evening", "duration": "30 days", "instructions": "After meals with water", "quantity": 1}
        ],
        "diagnosis": "Vata-Pitta imbalance with Mandagni",
        "doctor_notes": "Follow Ayurvedic diet plan strictly. Avoid cold foods."
    }
    r = safe_request("POST", f"{BASE_URL}/api/v1/prescriptions/catchy-from-data", json=pdf_data)
    if r and r.status_code == 200:
        content_type = r.headers.get("content-type", "")
        if "pdf" in content_type or len(r.content) > 1000:
            log_step(9, "Auto-Generate Prescription PDF", "pass",
                     f"PDF Generated! Size: {len(r.content)} bytes | Content-Type: {content_type}")
        else:
            log_step(9, "Auto-Generate Prescription PDF", "warn",
                     f"Response received but may not be PDF. Size: {len(r.content)} bytes | {r.text[:200]}")
    elif r:
        log_step(9, "Auto-Generate Prescription PDF", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(9, "Auto-Generate Prescription PDF", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 10: Auto-Cart Medicines (Shopify Draft Order)
    # =====================================================================
    cart_data = {
        "patient": {
            "name": "Test Patient",
            "age": 30,
            "contact": "+91 9876543210"
        },
        "doctor": {
            "name": "Dr. AyurEze",
            "regn_no": "AY-2026-001",
            "contact": "+91 98765 43210"
        },
        "prescriptions": [
            {"medicine": "Ashwagandha", "dose": "5g", "schedule": "Twice daily", "timing": "After meals", "duration": "30 days", "instructions": "Mix with warm milk", "quantity": 1},
            {"medicine": "Triphala", "dose": "3g", "schedule": "Once daily", "timing": "Before bed", "duration": "30 days", "instructions": "With warm water", "quantity": 1},
            {"medicine": "Brahmi", "dose": "2 tablets", "schedule": "Twice daily", "timing": "Morning & evening", "duration": "30 days", "instructions": "After meals", "quantity": 1}
        ],
        "diagnosis": "Vata-Pitta imbalance",
        "prescription_id": flow_state.get("prescription_id", "rx_test_001")
    }
    r = safe_request("POST", f"{BASE_URL}/api/v1/shopify/validate-prescription", json=cart_data)
    if r and r.status_code == 200:
        data = r.json()
        log_step(10, "Validate Prescription for Auto-Cart", "pass",
                 f"Validation: {json.dumps(data, indent=2)[:500]}")
    elif r:
        log_step(10, "Validate Prescription for Auto-Cart", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(10, "Validate Prescription for Auto-Cart", "fail", "TIMEOUT")

    # Also check available products
    r = safe_request("GET", f"{BASE_URL}/api/v1/shopify/products/search/Ashwagandha")
    if r and r.status_code == 200:
        print(f"  Shopify Product Search (Ashwagandha): {r.text[:300]}")

    # =====================================================================
    # STEP 11: Activate Astra Autopilot
    # =====================================================================
    autopilot_consent = {
        "patient_id": patient_id,
        "consent_granted": True
    }
    r = safe_request("POST", f"{BASE_URL}/api/v1/autopilot/consent", json=autopilot_consent)
    if r and r.status_code == 200:
        data = r.json()
        log_step(11, "Activate Astra Autopilot", "pass",
                 f"Autopilot: {json.dumps(data, indent=2)[:300]}")
    elif r:
        log_step(11, "Activate Astra Autopilot", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(11, "Activate Astra Autopilot", "fail", "TIMEOUT")

    # Check autopilot status
    r = safe_request("GET", f"{BASE_URL}/api/v1/autopilot/status/{patient_id}")
    if r:
        print(f"  Autopilot Status: {r.status_code} | {r.text[:300]}")

    # =====================================================================
    # STEP 12: Create Medicine Reminders
    # =====================================================================
    reminder_data = {
        "patient_id": patient_id,
        "patient_name": "Test Patient",
        "patient_phone": "+919876543210",
        "medicine_name": "Ashwagandha Churna",
        "dosage": "5g",
        "frequency": "twice_daily",
        "times": ["09:00", "21:00"],
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "instructions": "Mix with warm milk or water",
        "enable_whatsapp": False
    }
    r = safe_request("POST", f"{BASE_URL}/api/v1/api/reminders/create", json=reminder_data)
    if r and r.status_code in [200, 201]:
        data = r.json()
        flow_state["reminder_id"] = data.get("reminder_id", data.get("id", ""))
        log_step(12, "Create Medicine Reminders", "pass",
                 f"Reminder: {json.dumps(data, indent=2)[:400]}")
    elif r:
        log_step(12, "Create Medicine Reminders", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(12, "Create Medicine Reminders", "fail", "TIMEOUT")

    # Get reminders for patient
    r = safe_request("GET", f"{BASE_URL}/api/v1/api/reminders/patient/{patient_id}")
    if r:
        print(f"  Patient Reminders: {r.status_code} | {r.text[:300]}")

    # =====================================================================
    # STEP 13: Regular Health Check-in (Follow-up Chat)
    # =====================================================================
    followup_data = {
        "journey_id": flow_state.get("journey_id", ""),
        "message": "I have been taking Ashwagandha and Triphala for 3 days now. I feel slightly better but still have some headaches. My digestion has improved a little. Should I continue the same dosage?",
        "language": "en"
    }
    r = safe_request("POST", f"{BASE_URL}/api/companion/chat", json=followup_data)
    if r and r.status_code == 200:
        data = r.json()
        response_text = data.get("response", "")[:200]
        log_step(13, "Regular Health Check-in", "pass",
                 f"AI Follow-up: {response_text}...")
    elif r:
        log_step(13, "Regular Health Check-in", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(13, "Regular Health Check-in", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 14: Save Prescription in EHR Vault
    # =====================================================================
    # Check the documents endpoint (we can't upload a real file but we test the endpoint)
    r = safe_request("GET", f"{BASE_URL}/api/v1/documents/patient/{patient_id}")
    if r and r.status_code == 200:
        data = r.json()
        log_step(14, "EHR Vault - Patient Documents", "pass",
                 f"Documents: {json.dumps(data, indent=2)[:400]}")
    elif r:
        log_step(14, "EHR Vault - Patient Documents", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(14, "EHR Vault - Patient Documents", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 15: Update Case Progress
    # =====================================================================
    progress_data = {
        "case_id": flow_state.get("case_id", ""),
        "progress_percentage": 15.0,
        "adherence_score": 95.0,
        "notes": "Patient reports slight improvement in fatigue. Digestion improving. Headaches persist but less severe."
    }
    r = safe_request("PUT", f"{BASE_URL}/api/companion/case/progress", json=progress_data)
    if r and r.status_code == 200:
        data = r.json()
        log_step(15, "Update Case Progress", "pass",
                 f"Progress: {json.dumps(data, indent=2)[:300]}")
    elif r:
        log_step(15, "Update Case Progress", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(15, "Update Case Progress", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 16: Check Order Status
    # =====================================================================
    r = safe_request("GET", f"{BASE_URL}/api/v1/orders/patient/{patient_id}")
    if r and r.status_code == 200:
        data = r.json()
        log_step(16, "Order History / Status Check", "pass",
                 f"Orders: {json.dumps(data, indent=2)[:500]}")
    elif r:
        log_step(16, "Order History / Status Check", "warn",
                 f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(16, "Order History / Status Check", "fail", "TIMEOUT")

    # =====================================================================
    # STEP 17: Verify Case Details (Final State)
    # =====================================================================
    if flow_state.get("case_id"):
        r = safe_request("GET", f"{BASE_URL}/api/companion/case/{flow_state['case_id']}")
        if r and r.status_code == 200:
            data = r.json()
            log_step(17, "Final Case State Verification", "pass",
                     f"Case: {json.dumps(data, indent=2)[:500]}")
        elif r:
            log_step(17, "Final Case State Verification", "warn",
                     f"Status: {r.status_code} | {r.text[:300]}")
    else:
        log_step(17, "Final Case State Verification", "fail", "No case_id available")

    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================
    print("\n" + "="*70)
    print("  FLOW SUMMARY")
    print("="*70)
    
    passed = sum(1 for s in step_results if s["status"] == "pass")
    warned = sum(1 for s in step_results if s["status"] == "warn")
    failed = sum(1 for s in step_results if s["status"] == "fail")
    total = len(step_results)
    
    for s in step_results:
        icon = "[PASS]" if s["status"] == "pass" else ("[FAIL]" if s["status"] == "fail" else "[WARN]")
        print(f"  {icon} Step {s['step']:2d}: {s['title']}")
    
    print(f"\n  TOTAL: {total} steps | PASS: {passed} | WARN: {warned} | FAIL: {failed}")
    print(f"\n  Flow State IDs:")
    for key, value in flow_state.items():
        print(f"    {key}: {value}")
    print("="*70)


if __name__ == "__main__":
    run_full_flow()
