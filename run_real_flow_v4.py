import asyncio
import os
import sys
import uuid
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
    print("ASTRA REAL-USER FLOW SIMULATION - FINAL VERIFICATION")
    print("="*50)

    # 1. User Setup
    USER_EMAIL = "d.subash2710@gmail.com"
    USER_NAME = "Subash"
    PATIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, USER_EMAIL))
    
    # 1.5 Doctor Setup (ensure doctor exists)
    DOCTOR_ID = "DOC-REAL-001"
    print(f"\n[STEP 1]: Provisioning Doctor & Patient", flush=True)
    
    # Create doctor if not exists to avoid FK error
    try:
        db_manager.client.table("doctors").upsert({
            "doctor_id": DOCTOR_ID,
            "name": "Dr. AyurEze AI",
            "specialty": "Ayurveda Expert",
            "regn_no": "AI-REAL-101",
            "phone": "+91 89689 68156",
            "available": True
        }).execute()
        print(f"   Doctor {DOCTOR_ID} ready.")
    except Exception as e:
        print(f"   Doctor check failed: {e}")

    # Provision Patient
    existing = await db_manager.get_patient_profile(PATIENT_ID)
    if existing:
        print(f"   Patient {USER_NAME} ready (Code: {existing.get('patient_code')})")
    else:
        print(f"   Creating patient profile...")
        await db_manager.client.table("patient_profiles").upsert({
            "patient_id": PATIENT_ID, "name": USER_NAME, "email": USER_EMAIL,
            "patient_code": f"AS-{uuid.uuid4().hex[:4].upper()}"
        }).execute()

    # 2. Astra Fill
    print(f"\n[STEP 2]: Astra Fill - AI Extraction", flush=True)
    pipeline = AstraPipeline()
    patient_input = "I've been feeling persistent back pain for about 2 weeks. It gets worse after my morning walk."
    extraction = await pipeline.extract_data(patient_input, """{"symptoms": "list", "duration": "string"}""")
    print(f"   AI Extraction: {extraction.get('extracted_data')}")

    # 4. Prescription Automation
    print("\n[STEP 4]: Automated Prescription Flow", flush=True)
    
    # Use GUARANTEED store products found in previous check
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name=USER_NAME, contact=USER_EMAIL, age=30),
        doctor=DoctorInfo(name="Dr. AyurEze AI", regn_no="AI-REAL-101", contact="+91-89689 68156"),
        diagnosis="Vata Imbalance - Joint Stiffness",
        prescriptions=[
            PrescriptionItem(
                medicine="Aadarisahacharadi Kashayam", dose="15ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="15 days"
            )
        ]
    )

    print(f"   RUNNING: Processing prescription and Shopify order...", flush=True)
    automation_result = await automated_prescription_service.process_prescription(
        prescription_data=presc_request,
        doctor_id=DOCTOR_ID,
        patient_id=PATIENT_ID
    )

    if automation_result.get("success"):
        print(f"   SUCCESS: Order created. URL: {automation_result.get('shopify_order', {}).get('invoice_url')}")
        print(f"   EHR Stored (PDF): {automation_result.get('pdf_url')}")
    else:
        print(f"   FAILURE Errors: {automation_result.get('errors')}")

    # 7. Asking AI Questions
    print(f"\n[STEP 7]: AI Interaction", flush=True)
    user_query = "Why did you prescribe Aadarisahacharadi Kashayam?"
    response = await pipeline.process_query(user_id=PATIENT_ID, message=user_query, history=[])
    print(f"   Patient: \"{user_query}\"")
    print(f"   AI: \"{response}\"")

    print("\n" + "="*50)
    print("FLOW COMPLETED SUCCESSFULLY")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_astra_scenario())
