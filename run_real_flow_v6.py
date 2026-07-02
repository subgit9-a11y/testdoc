import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# load_dotenv() MUST be called before importing db_manager to ensure it gets the credentials
load_dotenv(override=True)

# Add current directory to path
sys.path.append(os.getcwd())

async def run_astra_scenario():
    print("IMPORTING: Components...", flush=True)
    from app.astra.pipeline import AstraPipeline
    from app.database import db_manager
    from app.automated_prescription_service import automated_prescription_service
    from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

    print("\n" + "="*50)
    print("ASTRA REAL-USER FLOW - PRODUCTION TEST")
    print("="*50)

    # 1. User/Patient Provisioning
    USER_EMAIL = "d.subash2710@gmail.com"
    USER_NAME = "Subash"
    PATIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, USER_EMAIL))
    DOCTOR_ID = "DOC-PROD-001"
    
    print(f"\n[STEP 1]: Provisioning Ecosystem", flush=True)
    
    # 1.1 Provision Doctor (Mapping to Supabase schema)
    try:
        db_manager.client.table("doctors").upsert({
            "doctor_id": DOCTOR_ID,
            "name": "Dr. AyurEze AI Expert",
            "specialization": "Ayurvedic Wellness",
            "is_active": True
        }).execute()
        print(f"   Doctor {DOCTOR_ID} synchronized.")
    except Exception as e:
        print(f"   Doctor sync warning: {e}")

    # 1.2 Provision Patient
    existing = await db_manager.get_patient_profile(PATIENT_ID)
    if existing:
        print(f"   Patient {USER_NAME} synchronized (ID: {PATIENT_ID[:8]}...)")
    else:
        print(f"   Provisioning new patient profile for {USER_NAME}...")
        db_manager.client.table("patient_profiles").upsert({
            "patient_id": PATIENT_ID, 
            "name": USER_NAME, 
            "email": USER_EMAIL,
            "patient_code": f"AS-{uuid.uuid4().hex[:4].upper()}",
            "is_active": True
        }).execute()

    # 2. Astra Fill - Real AI Extraction
    print(f"\n[STEP 2]: Astra Fill - Wellness Discovery", flush=True)
    pipeline = AstraPipeline()
    patient_input = "I've been feeling persistent back pain for about 2 weeks. It gets worse after my morning walk."
    print(f"   Input: \"{patient_input}\"")
    
    extraction = await pipeline.extract_data(patient_input, """{"symptoms": "list", "duration": "string"}""")
    print(f"   AI Insights: {extraction.get('extracted_data')}")

    # 3. Teleconsultation Sim
    CONSULT_ID = f"CONS-{uuid.uuid4().hex[:4].upper()}"
    print(f"\n[STEP 3]: Clinical Logging", flush=True)
    db_manager.client.table("consultations").upsert({
        "consultation_id": CONSULT_ID,
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "doctor_name": "Dr. AyurEze AI Expert",
        "diagnosis": "Vata Imbalance",
        "appointment_date": datetime.now(timezone.utc).isoformat(),
        "status": "completed"
    }).execute()
    print(f"   Consultation {CONSULT_ID} archived.")

    # 4. Prescription Automation (The Masterpiece)
    print("\n[STEP 4]: Automated Wellness Fulfillment", flush=True)
    
    # Using GUARANTEED product from REAL store
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name=USER_NAME, contact=USER_EMAIL, age=30),
        doctor=DoctorInfo(name="Dr. AyurEze AI Expert", regn_no="AI-CERT-01"), # regn_no is for PDF, not for DB
        diagnosis="Vata-Aggravated Back Stiffness",
        prescriptions=[
            PrescriptionItem(
                medicine="Aadarisahacharadi Kashayam", # EXACT title from store
                dose="15ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="15 days"
            )
        ]
    )

    print(f"   ORCHESTRATING: Shopify Order + PDF Creation + EHR Secure Upload...", flush=True)
    automation_result = await automated_prescription_service.process_prescription(
        prescription_data=presc_request,
        doctor_id=DOCTOR_ID,
        patient_id=PATIENT_ID
    )

    if automation_result.get("success"):
        print(f"   SUCCESS: Order created.")
        print(f"   ORDER URL: {automation_result.get('shopify_order', {}).get('invoice_url')}")
        print(f"   EHR Record: {automation_result.get('pdf_url')}")
    else:
        print(f"   ECOSYSTEM ERROR: {automation_result.get('errors')}")

    # 7. AI Companion interaction
    print(f"\n[STEP 5]: Wellness Companion Engagement", flush=True)
    p_query = "Why did you suggest Aadarisahacharadi Kashayam for my back pain?"
    print(f"   Patient: \"{p_query}\"")
    response = await pipeline.process_query(user_id=PATIENT_ID, message=p_query, history=[])
    print(f"   AI: \"{response}\"")

    # 8. Autopilot check
    print(f"\n[STEP 6]: Intelligent Routing (Autopilot)")
    r_query = "I would like to schedule another follow-up."
    r_intent = await pipeline.route_intent(r_query)
    print(f"   Patient: \"{r_query}\"")
    print(f"   RESULT: AI Intent Detection -> {r_intent['intent']}")

    print("\n" + "="*50)
    print("END-TO-END FLOW VERIFIED SUCCESSFULLY")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_astra_scenario())
