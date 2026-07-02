import requests
import json
import uuid
import time

BASE_URL = "https://astra.ayureze.in"
API_KEY = "astra-secret-2026"  # Default secret from codebase
HEADERS = {
    "X-API-Key": API_KEY,
    "Authorization": "Bearer dummy_token_for_test",
    "Content-Type": "application/json"
}

def log_step(step, name):
    print(f"\n--- [STEP {step}]: {name} ---")

def run_mock_flow():
    success_count = 0
    total_steps = 5

    try:
        # Step 1: Health Check
        log_step(1, "Basic Health Check")
        r = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.status_code == 200: success_count += 1

        # Step 2: Astra Fill - Text Processing
        log_step(2, "Astra Fill (Mock Intake)")
        fill_data = {
            "text": "I have been suffering from a sore throat and mild fever for the past 2 days. My head feels heavy.",
            "user_id": f"test-user-{uuid.uuid4().hex[:6]}"
        }
        # Based on routes.py, it's Form data
        r = requests.post(f"{BASE_URL}/api/v1/astra-fill/process-text", data=fill_data, headers={"X-API-Key": API_KEY})
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Extraction Success: {r.json().get('status')}")
            success_count += 1
        else:
            print(f"Error: {r.text}")

        # Step 3: AI Brain Chat (Knowledge Retrieval)
        log_step(3, "AI Brain Knowledge Bridge")
        chat_data = {"q": "What are the common benefits of Triphala?"}
        r = requests.post(f"{BASE_URL}/api/v1/brain/chat", json=chat_data, headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Brain Answer: {r.json().get('answer')[:100]}...")
            success_count += 1
        else:
            print(f"Error: {r.text}")

        # Step 4: Dosage Suggestion (AI Recommendation)
        log_step(4, "AI Dosage Optimization")
        dosage_data = {
            "medicine_name": "Ashwagandha",
            "patient_age": 35,
            "patient_gender": "Male",
            "symptoms": ["Anxiety", "Sleep issues"]
        }
        r = requests.post(f"{BASE_URL}/api/v1/api/prescriptions/suggest-dosage", json=dosage_data, headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Suggested Dosage: {r.json().get('suggested_dosage')}")
            success_count += 1
        else:
            print(f"Error: {r.text}")

        # Step 5: Prescription Creation (Unified Flow)
        log_step(5, "Full Prescription Lifecycle")
        presc_data = {
            "patient_id": "subashtest",
            "patient_name": "Test Patient",
            "patient_phone": "+919876543210",
            "doctor_id": "DOC-AI-01",
            "diagnosis": "Generalized Wellness Improvement",
            "medicines": [
                {
                    "name": "Sahacharadi Kashayam",
                    "dosage": "10ml",
                    "frequency": "twice_daily",
                    "duration_days": 15,
                    "instructions": "Before food with warm water"
                }
            ],
            "auto_process": True
        }
        r = requests.post(f"{BASE_URL}/api/v1/api/prescriptions/create", json=presc_data, headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            resp = r.json()
            print(f"Prescription Created! ID: {resp.get('prescription_id')}")
            print(f"Automation Status: {resp.get('automation', {}).get('success', False)}")
            success_count += 1
        else:
            print(f"Error: {r.text}")

        print(f"\n{'='*40}")
        print(f"MOCK FLOW SUMMARY: {success_count}/{total_steps} Passed")
        print(f"{'='*40}")

    except Exception as e:
        print(f"Critical Flow Error: {e}")

if __name__ == "__main__":
    run_mock_flow()
