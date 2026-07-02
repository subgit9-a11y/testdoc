import requests
import time

BASE_URL = "https://astra.ayureze.in"

# List of endpoints extracted previously
endpoints_raw = """
DELETE /api/v1/api/doctors/{doctor_id}
DELETE /api/v1/api/prescriptions/{prescription_id}
DELETE /api/v1/api/treatment-centers/{center_id}
DELETE /api/v1/documents/{document_id}
DELETE /api/v1/notifications/remove-fcm-token/{patient_id}
GET /
GET /admin/dashboard
GET /api/admin/config
GET /api/admin/logs
GET /api/admin/stats
GET /api/companion/case/{case_id}
GET /api/companion/conversation/{user_id}
GET /api/companion/journey/user/{user_id}
GET /api/companion/journey/{journey_id}
GET /api/companion/journey/{journey_id}/records
GET /api/companion/v2/health
GET /api/companion/v2/journey/{journey_id}
GET /api/companion/v2/voices
GET /api/v1/api/ai-agent/status
GET /api/v1/api/doctors/nearby/search
GET /api/v1/api/doctors/{doctor_id}
GET /api/v1/api/doctors/{doctor_id}/dashboard-stats
GET /api/v1/api/prescriptions/patient/{patient_id}
GET /api/v1/api/prescriptions/queue/pending
GET /api/v1/api/prescriptions/status
GET /api/v1/api/prescriptions/{prescription_id}
GET /api/v1/api/prescriptions/{prescription_id}/summary
GET /api/v1/api/translate/language-pairs
GET /api/v1/api/translate/languages
GET /api/v1/api/translate/status
GET /api/v1/api/treatment-centers/nearby/search
GET /api/v1/api/treatment-centers/{center_id}
GET /api/v1/astra-fill/patient/{user_id}/history
GET /api/v1/astra-fill/patient/{user_id}/latest
GET /api/v1/astra-fill/patient/{user_id}/records
GET /api/v1/auth/health
GET /api/v1/auth/user
GET /api/v1/brain/health
GET /api/v1/chat/sessions
GET /api/v1/documents/download/{document_id}
GET /api/v1/documents/metadata/{document_id}
GET /api/v1/documents/patient/{patient_id}
GET /api/v1/documents/share-link/{document_id}
GET /api/v1/health
GET /api/v1/notifications/service-status
GET /api/v1/notifications/test-notification/{patient_id}
GET /api/v1/patients/profile/{patient_id}
GET /api/v1/patients/search/{search_term}
GET /api/v1/patients/verify/{patient_code}
GET /api/v1/shopify/draft-order/{draft_order_id}
GET /api/v1/shopify/health
GET /api/v1/shopify/order-details/{draft_order_id}
GET /api/v1/shopify/products/available
GET /api/v1/shopify/products/search/{medicine_name}
GET /health
POST /api/companion/case/create
POST /api/companion/chat
POST /api/companion/journey/start
POST /api/companion/journey/{journey_id}/link-record
POST /api/companion/milestone/add
POST /api/companion/v2/chat
POST /api/companion/v2/journey/start
POST /api/v1/api/ai-agent/ask
POST /api/v1/api/ai-agent/batch
POST /api/v1/api/doctors/register
POST /api/v1/api/doctors/{doctor_id}/withdraw
POST /api/v1/api/prescriptions/create
POST /api/v1/api/prescriptions/draft
POST /api/v1/api/prescriptions/suggest-dosage
POST /api/v1/api/prescriptions/{prescription_id}/approve
POST /api/v1/api/prescriptions/{prescription_id}/process
POST /api/v1/api/prescriptions/{prescription_id}/reject
POST /api/v1/api/translate/
POST /api/v1/api/translate/auto-translate
POST /api/v1/api/translate/batch
POST /api/v1/api/treatment-centers/create
POST /api/v1/astra-fill/confirm
POST /api/v1/astra-fill/confirm-chat
POST /api/v1/astra-fill/confirm-transcript
POST /api/v1/astra-fill/process-text
POST /api/v1/astra-fill/process-voice
POST /api/v1/astra-fill/transcribe-chat
POST /api/v1/astra-fill/transcribe-voice
POST /api/v1/astra-fill/voice-assistant
POST /api/v1/auth/logout
POST /api/v1/auth/session
POST /api/v1/brain/adjust_tone
POST /api/v1/brain/analyze_safety
POST /api/v1/brain/chat
POST /api/v1/brain/doctor_summary
POST /api/v1/brain/extract_schedule
POST /api/v1/brain/shop_assist
POST /api/v1/chat/history
POST /api/v1/chat/message
POST /api/v1/documents/share-whatsapp/{document_id}
POST /api/v1/documents/upload
POST /api/v1/medicine-reminders/create-from-prescription
POST /api/v1/medicine-reminders/send-pending
POST /api/v1/notifications/store-fcm-token
POST /api/v1/notifications/test
POST /api/v1/patients/register
POST /api/v1/prescription-workflow/execute
POST /api/v1/prescriptions/auto-generate-catchy
POST /api/v1/prescriptions/catchy-from-data
POST /api/v1/prescriptions/catchy-from-upload
POST /api/v1/shopify/ai-shop-assist
POST /api/v1/shopify/draft-order
POST /api/v1/shopify/real-order-cod
POST /api/v1/shopify/validate-prescription
POST /astra/chat
PUT /api/companion/case/progress
PUT /api/companion/journey/{journey_id}/status
PUT /api/v1/api/doctors/{doctor_id}
PUT /api/v1/api/prescriptions/{prescription_id}
PUT /api/v1/api/treatment-centers/{center_id}
"""

HEADERS = {
    "X-API-Key": "astra-secret-2026",
    "Authorization": "Bearer dummy_token_for_test",
    "Content-Type": "application/json"
}

working = []
failing = []

def process_path(path):
    # Replace path parameters with dummy values
    import re
    return re.sub(r'\{[^}]+\}', 'test-123', path)

print("Starting endpoint sweep. This may take a moment...")

for line in endpoints_raw.strip().split('\n'):
    if not line:
        continue
    method, path = line.split(' ', 1)
    test_path = process_path(path)
    url = f"{BASE_URL}{test_path}"
    
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=5)
        elif method == "POST":
            # Send an empty JSON dict which will fail Pydantic validation (422) if body is required,
            # but proves the endpoint is alive.
            r = requests.post(url, json={}, headers=HEADERS, timeout=5)
        elif method == "PUT":
            r = requests.put(url, json={}, headers=HEADERS, timeout=5)
        elif method == "DELETE":
            r = requests.delete(url, headers=HEADERS, timeout=5)
            
        # 500 means Internal Server Error (usually unhandled exception like missing DB table or bad input that bypassed validation)
        # 502/503/504 means Gateway errors (container crashed or unresponsive)
        # 422 means Unprocessable Entity (FastAPI is alive and validating input)
        # 401/403 means Unauthorized (FastAPI is alive and protecting endpoint)
        # 404/405 means Not Found / Method Not Allowed (FastAPI is routing)
        if r.status_code >= 500:
            failing.append(f"{method} {path} => {r.status_code} {r.reason}")
        else:
            working.append(f"{method} {path} => {r.status_code} {r.reason}")
            
    except requests.exceptions.RequestException as e:
        failing.append(f"{method} {path} => TIMEOUT/ERROR: {type(e).__name__}")
    
    time.sleep(0.05)  # small delay to prevent overloading Nginx

print("\n" + "="*50)
print(f"WORKING ENDPOINTS ({len(working)}):")
print("These are successfully reaching the backend and returning valid HTTP routing/validation responses (200s, 401s, 422s, etc.)")
print("="*50)
for w in working:
    print(w)

print("\n" + "="*50)
print(f"FAILING/CRASHING ENDPOINTS ({len(failing)}):")
print("These are returning 500 Internal Server Error (crashes due to bad dummy data/missing DB) or 502 Gateway Errors.")
print("="*50)
for f in failing:
    print(f)
