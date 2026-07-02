import asyncio
import json
import os
import sys
import uuid
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

# Configure logging to see internal errors
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def run_astra_scenario():
    print("IMPORTING: Components...", flush=True)
    try:
        from app.astra_brain_client import get_brain_client
        from app.astra.pipeline import AstraPipeline
        from app.database import db_manager
        from app.wasabi_client import WasabiClient
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return

    print("\n" + "="*50)
    print("ASTRA REAL-USER FLOW SIMULATION")
    print("="*50)

    # 1. User Setup
    USER_EMAIL = "d.subash2710@gmail.com"
    USER_NAME = "Subash"
    CASE_ID = "CASE_REAL_002"
    PATIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, USER_EMAIL))
    
    print(f"\n[STEP 1]: User Login & Provisioning", flush=True)
    print(f"   Patient: {USER_NAME} ({USER_EMAIL})")
    print(f"   Patient ID: {PATIENT_ID}")
    
    existing = await db_manager.get_patient_profile(PATIENT_ID)
    if existing:
        print(f"   SUCCESS: Real user found. Code: {existing.get('patient_code', 'N/A')}")
    else:
        print(f"   INFO: Creating profile...")
        await db_manager.upsert_user({"user_id": PATIENT_ID, "email": USER_EMAIL, "name": USER_NAME, "email_verified": True})
        await db_manager.client.table("patient_profiles").upsert({
            "patient_id": PATIENT_ID,
            "name": USER_NAME,
            "email": USER_EMAIL,
            "phone": "+91 89689 68156",
            "patient_code": f"AS-{uuid.uuid4().hex[:4].upper()}"
        }).execute()

    # 2. Astra Fill
    print(f"\n[STEP 2]: Astra Fill - AI Extraction", flush=True)
    pipeline = AstraPipeline()
    patient_input = "I've been feeling persistent back pain for about 2 weeks. It gets worse after my morning walk."
    print(f"   Input: \"{patient_input}\"")
    
    extraction = await pipeline.extract_data(patient_input, """{"symptoms": "list", "duration": "string"}""")
    print(f"   AI Extraction: {extraction.get('extracted_data')}")

    # 4. Prescription Automation (Directly using valid Shopify keys)
    print("\n[STEP 4]: Automated Prescription Flow", flush=True)
    from app.automated_prescription_service import automated_prescription_service
    from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem
    
    # Using EXACT keys from all_products_mapping.py
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name=USER_NAME, contact=USER_EMAIL, age=30),
        doctor=DoctorInfo(name="Dr. AyurEze AI", regn_no="AI-REAL-101", contact="+91-89689 68156"),
        diagnosis="Vata Imbalance - Joint Stiffness",
        prescriptions=[
            PrescriptionItem(
                medicine="mahanarayana tailam", dose="5ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="21 days"
            ),
            PrescriptionItem(
                medicine="aswagandha choornam", dose="1 tsp", quantity=1,
                schedule="Once daily", timing="Before sleep", duration="14 days"
            )
        ]
    )

    print(f"   RUNNING: Processing prescription and Shopify Draft Order...", flush=True)
    automation_result = await automated_prescription_service.process_prescription(
        prescription_data=presc_request,
        doctor_id="DOC-REAL-101",
        patient_id=PATIENT_ID
    )

    if automation_result["success"]:
        print(f"   SUCCESS: Order created. URL: {automation_result['shopify_order']['invoice_url']}")
        print(f"   EHR Stored (PDF): {automation_result['pdf_url']}")
    else:
        print(f"   FAILURE: {automation_result.get('errors')}")

    # 7. Asking AI Questions
    print(f"\n[STEP 7]: Questioning the AI", flush=True)
    user_query = "Why did you prescribe Mahanarayana Tailam for my symptoms?"
    print(f"   Patient: \"{user_query}\"")
    response = await pipeline.process_query(user_id=PATIENT_ID, message=user_query, history=[])
    print(f"   AI: \"{response}\"")

    # 8. Autopilot
    print(f"\n[STEP 8]: Autopilot Routing", flush=True)
    route_query = "I want to shop for more Ayurvedic products."
    print(f"   Patient: \"{route_query}\"")
    route = await pipeline.route_intent(route_query)
    print(f"   RESULT: Intent -> {route['intent']}")

    print("\n" + "="*50)
    print("FLOW COMPLETED SUCCESSFULLY")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_astra_scenario())
