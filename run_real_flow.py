import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

async def run_astra_scenario():
    print("IMPORTING: AstraBrainClient, AstraPipeline, db_manager, WasabiClient...")
    try:
        from app.astra_brain_client import get_brain_client
        from app.astra.pipeline import AstraPipeline
        from app.database import db_manager
        from app.wasabi_client import WasabiClient
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return

    print("\n" + "="*50)
    print("ASTRA WELLNESS COMPANION - FULL SCENARIO")
    print("="*50)

    # 1. User Setup
    USER_EMAIL = "d.subash2710@gmail.com"
    USER_NAME = "Subash"
    CASE_ID = "CASE_REAL_001"
    # Unified UID from email for consistency
    PATIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, USER_EMAIL))
    
    print(f"\n[STEP 1]: User Login & Provisioning")
    print(f"   Patient: {USER_NAME} ({USER_EMAIL})")
    print(f"   Patient ID: {PATIENT_ID}")
    
    # Check if user already exists
    existing = await db_manager.get_patient_profile(PATIENT_ID)
    if existing:
        print(f"   SUCCESS: Real user found in database.")
    else:
        print(f"   INFO: User not found in patient_profiles. Upserting...")
        user_data = {
            "user_id": PATIENT_ID,
            "email": USER_EMAIL,
            "name": USER_NAME,
            "email_verified": True
        }
        await db_manager.upsert_user(user_data)
        
        profile_data = {
            "patient_id": PATIENT_ID,
            "name": USER_NAME,
            "email": USER_EMAIL,
            "phone": "+91 99999 88888",
            "patient_code": f"AS-{uuid.uuid4().hex[:4].upper()}"
        }
        if db_manager.client:
            try:
                db_manager.client.table("patient_profiles").upsert(profile_data).execute()
                print("   SUCCESS: User database records ready.")
            except Exception as e:
                print(f"   WARNING: Profile upsert error: {e}")
    
    # 2. Astra Fill (Health detail extraction)
    print(f"\n[STEP 2]: Astra Fill - Real Patient Health Intake")
    pipeline = AstraPipeline()
    patient_input = "I've been feeling persistent back pain and knee stiffness for about 2 weeks. It gets worse after my morning walk."
    print(f"   Input: \"{patient_input}\"")
    
    print("   RUNNING: AI Extraction...", flush=True)
    extraction = await pipeline.extract_data(patient_input, """{
        "symptoms": "list of strings",
        "duration": "string",
        "pain_aggravated_by": "string"
    }""")
    print(f"   SUCCESS: Extraction Result: {extraction.get('extracted_data')}")

    # 1.5. Doctor Setup
    DOCTOR_ID = "DOC-REAL-001"
    print(f"\n[STEP 1.5]: Doctor Setup ({DOCTOR_ID})")
    if db_manager.client:
        try:
            db_manager.client.table("doctors").upsert({
                "doctor_id": DOCTOR_ID,
                "name": "Dr. AyurEze AI Specialist",
                "specialization": "Ayurveda Consultation"
            }).execute()
            print("   SUCCESS: Doctor profile ready.")
        except Exception as e:
            print(f"   Note: Doctor upsert failed: {e}")

    # 3. Teleconsultation
    print(f"\n[STEP 3]: Teleconsultation Documentation")
    consultation_id = f"CONS-REAL-{uuid.uuid4().hex[:4].upper()}"
    consultation_data = {
        "consultation_id": consultation_id,
        "patient_id": PATIENT_ID,
        "doctor_id": DOCTOR_ID,
        "doctor_name": "Dr. AyurEze AI Specialist",
        "complaints": patient_input, 
        "status": "completed",
        "diagnosis": "Vata accumulation in Sandhi (Joints)",
        "appointment_date": datetime.now(timezone.utc).isoformat(),
        "notes": "Suggest Mahanarayan Oil and Ashwagandha tablets."
    }
    try:
        cid = await db_manager.create_consultation(consultation_data)
        print(f"   SUCCESS: Consultation record created: {cid if cid else consultation_id}")
    except Exception as e:
        print(f"   WARNING: Consultation DB insert failed, proceeding with flow.")

    # Step 4: Full Automation (Prescription -> Shopify -> PDF -> Wasabi)
    print("\n[STEP 4]: Smart Auto Cart & Prescription Automation")
    try:
        from app.automated_prescription_service import automated_prescription_service
        from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem
        
        presc_request = PrescriptionRequest(
            patient=PatientInfo(name=USER_NAME, contact=USER_EMAIL, age=30),
            doctor=DoctorInfo(name="Dr. AyurEze AI Specialist", regn_no="AI-REAL-001", contact="+91-89689 68156"),
            diagnosis=consultation_data["diagnosis"],
            prescriptions=[
                PrescriptionItem(
                    medicine="Mahanarayan Oil", dose="5ml", quantity=1,
                    schedule="Twice daily", timing="Morning and Night",
                    instructions="Apply locally on joints", duration="21 days"
                ),
                PrescriptionItem(
                    medicine="Ashwagandha", dose="1 tab", quantity=1,
                    schedule="Once daily", timing="After dinner",
                    instructions="Take with milk", duration="14 days"
                )
            ]
        )

        print(f"   RUNNING: Executing Full Automated Prescription Flow...")
        automation_result = await automated_prescription_service.process_prescription(
            prescription_data=presc_request,
            doctor_id=DOCTOR_ID,
            patient_id=PATIENT_ID
        )

        if automation_result["success"]:
            prescription_id = automation_result['prescription_id']
            print(f"   SUCCESS: Prescription {prescription_id} created.")
            print(f"   Shopify: Draft Order {automation_result['shopify_order']['draft_order_id']} ready.")
            print(f"   Invoice: {automation_result['shopify_order']['invoice_url']}")
            print(f"   Wasabi Store: {automation_result['pdf_url']}")
        else:
            print(f"   FAILURE: Automation errors: {automation_result.get('errors')}")
    except Exception as e:
        print(f"   ERROR in Automation step: {e}")

    # Step 5: Auto Smart Cart Suggestion
    print("\n[STEP 5]: Auto Smart Cart Suggestion")
    shop_query = "Ayurvedic oils for joint pain and stiffness"
    print(f"   RUNNING: Shop Assist for query: \"{shop_query}\"")
    recommendations = await pipeline.get_shop_recommendations(shop_query)
    print(f"   SUCCESS: AI Recommendations: {recommendations.get('result')}")

    # Step 6: EHR Document Check
    print("\n[STEP 6]: EHR Document & Storage Check")
    docs = await db_manager.get_patient_documents(PATIENT_ID)
    if docs:
        print(f"   SUCCESS: Found {len(docs)} documents for patient in EHR.")
        latest_doc = docs[0]
        print(f"   Latest: {latest_doc['original_filename']} via {latest_doc.get('storage_provider', 'storage')}")
    else:
        print("   INFO: No document records found for this patient yet.")

    # 7. Astra Companion Real-time Interaction
    print(f"\n[STEP 7]: Astra Companion Real-time AI Interaction")
    user_query = "Hey Astra, can you explain why Mahanarayan Oil is good for my joint pain?"
    print(f"   Patient: \"{user_query}\"")
    
    print("   RUNNING: AI Thoughts...", flush=True)
    response = await pipeline.process_query(user_id=PATIENT_ID, message=user_query, history=[])
    print(f"   ASTRA: \"{response}\"")
    
    # Step 8: Astra Autopilot Intent Routing
    print(f"\n[STEP 8]: Astra Autopilot - Intent Routing")
    route_queries = [
        "I need to book a follow up consultation",
        "How can I see my last prescription?"
    ]
    for rq in route_queries:
        print(f"   Patient: \"{rq}\"")
        route = await pipeline.route_intent(rq)
        print(f"   RESULT: Intent -> {route['intent']} (Should Route: {route['should_route']})")

    print("\n" + "="*50)
    print("FULL REAL-USER SCENARIO COMPLETED")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_astra_scenario())
