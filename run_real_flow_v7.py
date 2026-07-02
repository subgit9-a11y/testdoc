import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# load_dotenv() MUST be called before importing components
load_dotenv(override=True)

# Add current directory to path
sys.path.append(os.getcwd())

async def run_astra_scenario():
    print("IMPORTING: Components...", flush=True)
    from app.astra.pipeline import AstraPipeline
    from app.database import db_manager
    from app.automated_prescription_service import automated_prescription_service
    from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

    print("\n" + "="*60)
    print("ASTRA REAL-USER FLOW - V7 (MOCK FLOW + REAL DB + DEBUG)")
    print("="*60)

    # 1. User/Patient Provisioning
    USER_EMAIL = "d.subash2710@gmail.com" # Real user email provided in previous flows
    USER_NAME = "Subash (Real Flow Test)"
    PATIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, USER_EMAIL))
    DOCTOR_ID = "DOC-PROD-001" # Real doctor ID from DB
    
    print(f"\n[STEP 1]: Provisioning/Verifying Ecosystem", flush=True)
    
    # 1.1 Provision/Verify Doctor in BOTH possible tables
    try:
        if db_manager.is_connected():
            # Try 'doctor_profiles' (used in service)
            db_manager.client.table("doctor_profiles").upsert({
                "doctor_id": DOCTOR_ID,
                "name": "Dr. AyurEze AI Expert",
                "specialization": "Ayurvedic Wellness",
                "is_active": True
            }).execute()
            print(f"   Doctor {DOCTOR_ID} synced in 'doctor_profiles'.")
            
            # Try 'doctors' (fallback/alternative)
            try:
                db_manager.client.table("doctors").upsert({
                    "doctor_id": DOCTOR_ID,
                    "name": "Dr. AyurEze AI Expert"
                }).execute()
                print(f"   Doctor {DOCTOR_ID} synced in 'doctors'.")
            except:
                pass # Table might not exist
        else:
            print("   WARNING: Database not connected (OFFLINE MODE)")
    except Exception as e:
        print(f"   Doctor sync warning: {e}")

    # 1.2 Provision/Verify Patient
    try:
        if db_manager.is_connected():
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
        else:
             print("   WARNING: Database offline, using local patient info.")
    except Exception as e:
        print(f"   Patient sync error: {e}")

    # 2. Astra Fill - Real AI Extraction
    print(f"\n[STEP 2]: Astra Fill - Wellness Introspection", flush=True)
    pipeline = AstraPipeline()
    patient_input = "Doctor, I've been having high fever and cold for 3 days. My body aches a lot."
    print(f"   AI Processing: \"{patient_input}\"")
    
    try:
        # Simulate extraction pipeline
        extraction = await pipeline.extract_data(patient_input, """{"symptoms": "list", "severity": "string"}""")
        print(f"   AI Extracted Data: {extraction.get('extracted_data')}")
    except Exception as e:
        print(f"   AI Extraction Error: {e}")

    # 3. Teleconsultation Registry
    CONSULT_ID = f"CONS-{uuid.uuid4().hex[:4].upper()}"
    print(f"\n[STEP 3]: Clinical Documentation (Consultation)", flush=True)
    try:
        if db_manager.is_connected():
            db_manager.client.table("consultations").upsert({
                "consultation_id": CONSULT_ID,
                "patient_id": PATIENT_ID,
                "doctor_id": DOCTOR_ID,
                "doctor_name": "Dr. AyurEze AI Expert",
                "diagnosis": "Jwara (Fever) & Pratishyaya (Cold)",
                "appointment_date": datetime.now(timezone.utc).isoformat(),
                "status": "completed"
            }).execute()
            print(f"   Consultation {CONSULT_ID} archived in Supabase.")
        else:
            print("   Consultation simulated (Offline).")
    except Exception as e:
        print(f"   Consultation logging error: {e}")

    # 4. Prescription Debugging Task
    print("\n[STEP 4]: Prescription Debugging & Fulfillment", flush=True)
    print("   TASK: Verify Shopify mapping + PDF generation + EHR storage.", flush=True)
    
    # We will test a medicine that should be in the Shopify shop
    # Mapping "Sahacharadi" or similar from shop
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name=USER_NAME, contact=USER_EMAIL, age=30),
        doctor=DoctorInfo(name="Dr. AyurEze AI Expert", regn_no="AI-CERT-01"),
        diagnosis="Jwara (Flu-like symptoms)",
        prescriptions=[
            PrescriptionItem(
                medicine="Sahacharadi Kashayam", # Standard Ayurvedic medicine
                dose="10ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="7 days",
                instructions="Mix with equal amount of warm water before food."
            )
        ],
        doctor_notes="Rest well and stay hydrated. Avoid cold drinks."
    )

    print(f"   PROCESSING: Orchestrating post-prescription workflow...", flush=True)
    automation_result = await automated_prescription_service.process_prescription(
        prescription_data=presc_request,
        doctor_id=DOCTOR_ID,
        patient_id=PATIENT_ID
    )

    if automation_result.get("success"):
        print(f"   ✅ SUCCESS: Prescription processed.")
        print(f"   - Prescription ID: {automation_result.get('prescription_id')}")
        print(f"   - Shopify Order URL: {automation_result.get('shopify_order', {}).get('invoice_url')}")
        print(f"   - EHR PDF Record: {automation_result.get('pdf_url')}")
        if automation_result.get("email_sent"):
            print(f"   - Status: Official email delivered to {USER_EMAIL}")
    else:
        print(f"   ❌ FAILED: Prescription processing error.")
        print(f"   - Errors: {automation_result.get('errors')}")

    # 5. AI Safety & Summary (Debug Connection to Brain)
    print(f"\n[STEP 5]: AI Brain Safety Check", flush=True)
    try:
        from app.brain_client import brain_client
        safety_analysis = await brain_client.analyze_medication_safety({
            "diagnosis": "Fever",
            "prescriptions": [{"medicine": "Sahacharadi Kashayam", "dosage": "10ml"}]
        })
        print(f"   Safety Analysis Result: {safety_analysis.get('is_safe', 'Unknown')}")
        if not safety_analysis.get('is_safe', True):
            print(f"   Warnings: {safety_analysis.get('warnings')}")
    except Exception as e:
        print(f"   Brain Client Connectivity Error: {e}")

    print("\n" + "="*60)
    print("V7 FLOW TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_astra_scenario())
