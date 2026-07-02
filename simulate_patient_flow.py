import requests
import json
import time
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://astra.ayureze.in"
HEADERS = {
    "X-API-Key": "astra-secret-2026",
    "Content-Type": "application/json"
}

def run_flow():
    print("--- ASTRA REAL PATIENT FLOW SIMULATION ---")
    
    print("Checking API health...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {r.status_code}")

    print("\n[PATIENT] Starting Companion Journey...")
    journey_data = {
        "user_id": "test_patient_123",
        "health_concern": "General fatigue and stress",
        "language": "en"
    }
    r = requests.post(f"{BASE_URL}/api/companion/journey/start", json=journey_data, headers=HEADERS)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        journey_id = r.json().get("journey_id")
        print(f"\nJourney ID: {journey_id}")
        
        print("\n[PATIENT] Sending Chat Message to Companion...")
        chat_data = {
            "journey_id": journey_id,
            "message": "I feel very tired today. Do you have any suggestions?",
            "language": "en"
        }
        r = requests.post(f"{BASE_URL}/api/companion/chat", json=chat_data, headers=HEADERS)
        print(f"Status: {r.status_code}")
        try:
            print(f"Response: {json.dumps(r.json(), indent=2)}")
        except:
            print(f"Response: {r.text}")
        
        print("\n[DOCTOR] Creating Case...")
        case_data = {
            "journey_id": journey_id,
            "user_id": "test_patient_123",
            "doctor_id": "dr_ayureze_test",
            "diagnosis": "Fatigue",
            "treatment_duration_days": 30
        }
        r = requests.post(f"{BASE_URL}/api/companion/case/create", json=case_data, headers=HEADERS)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            case_id = r.json().get("case_id")
            print(f"\n[SYSTEM] Retrieving Case details: {case_id}")
            r = requests.get(f"{BASE_URL}/api/companion/case/{case_id}", headers=HEADERS)
            print(f"Status: {r.status_code}")
            try:
                print(f"Response: {json.dumps(r.json(), indent=2)}")
            except:
                print(f"Response: {r.text}")

if __name__ == "__main__":
    run_flow()
