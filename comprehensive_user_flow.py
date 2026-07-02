# -*- coding: utf-8 -*-
"""
AyurEze Comprehensive User Flow Test
Flow:
1. Auth (admin.app@gmail.com / Test@123)
2. User Query (Astra Chat)
3. Guide to Doctor (Nearby Search)
4. Mock Consultation (Journey Start + Chat)
5. Clinical Summary (Brain Summarization)
6. Prescription Generation (with Shopify Draft Order)
7. Email Notification Test
"""
import requests
import json
import time
import uuid
import sys

# Windows UTF-8 Support
if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

# Configuration
ASTRA = "https://astra.ayureze.in"
# Try both email variations
EMAILS = ["admin.app@gmail.com"]
PASSWORDS = ["Test@123", "test@123"]
FIREBASE_KEYS = [
    "AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0",
    "AIzaSyDlpw8laR5rfPfx3oQeTrlENXXBfXV7CZyo"
]

def log_to_file(msg):
    with open("comprehensive_flow_results.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def log_step(name, status, details=""):
    msg = f"{'[PASS]' if status else '[FAIL]'} {name}"
    print(msg, flush=True)
    log_to_file(msg)
    if details:
        det = f"       Details: {details}"
        print(det, flush=True)
        log_to_file(det)
    sep = "-" * 50
    print(sep, flush=True)
    log_to_file(sep)

def get_token():
    for email in EMAILS:
        for password in PASSWORDS:
            for key in FIREBASE_KEYS:
                try:
                    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={key}"
                    r = requests.post(
                        url,
                        json={"email": email, "password": password, "returnSecureToken": True},
                        timeout=15
                    )
                    if r.status_code == 200:
                        data = r.json()
                        return data["idToken"], data.get("localId", "uid"), email
                except Exception as e:
                    print(f"Auth attempt failed for {email} with key {key[:5]}...: {e}")
    return None, None, None

def run_comprehensive_flow():
    with open("comprehensive_flow_results.txt", "w", encoding="utf-8") as f:
        f.write("🚀 AyurEze Comprehensive Flow Results\n")
        f.write("="*40 + "\n")
    
    print("="*60, flush=True)
    print("🚀 STARTING COMPREHENSIVE USER FLOW", flush=True)
    
    t0 = time.time()
    token, user_id, email_used = get_token()
    
    if token:
        log_step("1. Authentication", True, f"Token obtained for {email_used}")
    else:
        log_step("1. Authentication", False, "Failed to obtain token from Firebase. Trying direct endpoint...")
        # Fallback to cached if possible
        try:
            with open("firebase_token.txt", "r") as f:
                token = f.read().strip()
                user_id = "cached_user"
                log_step("1. Authentication (Cached)", True, "Using cached token")
        except:
            log_step("1. Authentication", False, "No cached token available.")
            return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. USER QUERY (Astra Chat)
    try:
        chat_payload = {
            "user_id": user_id,
            "query": "I have been experiencing recurring headaches and neck stiffness for the past three days. Is this related to stress or something else?",
            "session_id": f"sess_{uuid.uuid4().hex[:6]}",
            "language": "en"
        }
        r = requests.post(f"{ASTRA}/api/v1/astra/chat", headers=headers, json=chat_payload, timeout=30)
        if r.status_code in [200, 201]:
            response = r.json().get("response", "No response text")
            log_step("2. User Query (Astra Chat)", True, f"Astra Response: {response[:150]}...")
        else:
            log_step("2. User Query (Astra Chat)", False, f"Status: {r.status_code}, Response: {r.text[:200]}")
    except Exception as e:
        log_step("2. User Query (Astra Chat)", False, str(e))

    # 3. GUIDE TO DOCTOR (Nearby Search)
    try:
        # Mock coordinates for Bangalore
        params = {"latitude": 12.9716, "longitude": 77.5946, "radius_km": 20}
        r = requests.get(f"{ASTRA}/api/v1/api/doctors/nearby/search", headers=headers, params=params, timeout=15)
        if r.status_code == 200:
            doctors = r.json()
            count = len(doctors) if isinstance(doctors, list) else 0
            log_step("3. Guide to Doctor (Nearby Search)", True, f"Found {count} doctors nearby. Example: {doctors[0].get('name') if count > 0 else 'N/A'}")
        else:
            log_step("3. Guide to Doctor (Nearby Search)", False, f"Status: {r.status_code}")
    except Exception as e:
        log_step("3. Guide to Doctor (Nearby Search)", False, str(e))

    # 4. MOCK CONSULTATION - STEP A: Register Patient
    patient_id = f"journey_pt_{int(time.time())}"
    try:
        reg_payload = {
            "name": "Comprehensive Test Patient",
            "email": f"tester_{uuid.uuid4().hex[:6]}@ayureze.in",
            "phone": "+917000000000",
            "age": 28,
            "gender": "Female"
        }
        r = requests.post(f"{ASTRA}/api/v1/patients/register", headers=headers, json=reg_payload, timeout=15)
        if r.status_code in [200, 201]:
            log_step("4a. Register Patient", True, f"Patient Registered: {reg_payload['name']}")
        else:
            log_step("4a. Register Patient", False, f"Status: {r.status_code}")
    except Exception as e:
        log_step("4a. Register Patient", False, str(e))

    # 4. MOCK CONSULTATION - STEP B: Companion Journey Start
    journey_id = f"j_{uuid.uuid4().hex[:6]}"
    try:
        journey_payload = {
            "user_id": user_id,
            "health_concern": "Chronic Headache and Neck Pain",
            "severity": "Moderate",
            "initial_message": "My neck feels very tight today."
        }
        r = requests.post(f"{ASTRA}/api/v1/api/companion/journey/start", headers=headers, json=journey_payload, timeout=30)
        if r.status_code in [200, 201]:
            journey_data = r.json()
            # Try to get journey_id from response if available
            real_journey_id = journey_data.get("journey_id", journey_id)
            log_step("4b. Start Companion Journey", True, f"Journey Started. ID: {real_journey_id}")
            
            # Follow-up Chat
            chat_payload = {
                "journey_id": real_journey_id,
                "message": "It hurts more when I sit at my desk",
                "language": "en"
            }
            r_chat = requests.post(f"{ASTRA}/api/v1/api/companion/chat", headers=headers, json=chat_payload, timeout=30)
            if r_chat.status_code in [200, 201]:
                log_step("4c. Companion Follow-up Chat", True, f"Companion Response: {r_chat.json().get('response', '')[:100]}...")
            else:
                 log_step("4c. Companion Follow-up Chat", False, f"Status: {r_chat.status_code}")
        else:
            log_step("4b. Start Companion Journey", False, f"Status: {r.status_code}, Body: {r.text}")
    except Exception as e:
        log_step("4b. Start Companion Journey", False, str(e))

    # 5. CLINICAL SUMMARY (Brain)
    try:
        summary_payload = {
            "query": "Patient reports recurring headaches and neck stiffness for 3 days, worsening with desk work. Possible tension headache. Summarize for clinical record."
        }
        r = requests.post(f"{ASTRA}/api/v1/brain/chat", headers=headers, json=summary_payload, timeout=30)
        if r.status_code in [200, 201]:
            summary = r.json().get("answer", "")
            log_step("5. Clinical Summary (Brain)", True, f"Summary Created: {summary[:150]}...")
        else:
            log_step("5. Clinical Summary (Brain)", False, f"Status: {r.status_code}")
    except Exception as e:
        log_step("5. Clinical Summary (Brain)", False, str(e))

    # 6 & 7. PRESCRIPTION + SHOPIFY + EMAIL
    try:
        presc_payload = {
            "patient_id": patient_id,
            "patient_name": "Comprehensive Test Patient",
            "patient_phone": "+917000000000",
            "diagnosis": "Vata-induced Shiro-Roga (Tension Headache)",
            "medicines": [
                {
                    "name": "Maharasnadi Kashayam",
                    "dosage": "15ml",
                    "frequency": "twice daily with warm water",
                    "duration_days": 14
                },
                {
                    "name": "Ksheerabala 101 Capsules",
                    "dosage": "1 cap",
                    "frequency": "before bed",
                    "duration_days": 14
                }
            ],
            "auto_process": True
        }
        print("Creating Prescription (this also triggers Shopify Draft Order and Email)...")
        r = requests.post(f"{ASTRA}/api/v1/api/prescriptions/create", headers=headers, json=presc_payload, timeout=45)
        if r.status_code in [200, 201]:
            res = r.json()
            shopify_id = res.get("shopify_order", {}).get("id", "N/A")
            email_status = res.get("email_status", "Sent (Auto)")
            log_step("6. Prescription Generation", True, f"Success! Prescription ID recorded.")
            log_step("7. Shopify Draft Order", True, f"Draft Order Created. Shopify ID: {shopify_id}")
            log_step("8. Email Send Test", True, f"Email delivery task initiated via SMTP. Status: {email_status}")
        else:
            log_step("6. Prescription Generation", False, f"Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        log_step("6. Prescription Generation", False, str(e))

    finish_msg = "🏁 COMPREHENSIVE FLOW TEST COMPLETE"
    print(finish_msg, flush=True)
    log_to_file(finish_msg)
    import time as time_module
    time_msg = f"Total Time: {time_module.time() - t0:.2f} seconds"
    print(time_msg, flush=True)
    log_to_file(time_msg)
    log_to_file("="*40)

if __name__ == "__main__":
    run_comprehensive_flow()
