
import asyncio
import os
import sys
import uuid
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

# Environment & Constants
load_dotenv()
sys_path = os.getcwd()
if sys_path not in sys.path: sys.path.append(sys_path)

from app.database import db_manager
from app.automated_prescription_service import automated_prescription_service
from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

async def complete_flow():
    print("\n" + "="*60)
    print("🚀 ASTRA END-TO-END DOCTOR PRESCRIPTION AUTOMATION")
    print("="*60)

    # 1. Selection
    DOCTOR_ID = "DOC-001"
    PATIENT_ID = "12b1d7b4-f4bb-57fe-86e6-fddad9e8b2bd"
    
    # 2. Retrieve & Verify Profiles
    print(f"\nStep 1: Retrieving Real Doctor & Patient Profiles...")
    
    # Retrieve Doctor
    doctor_res = await db_manager.client.table('doctors').select('*').eq('doctor_id', DOCTOR_ID).execute()
    if doctor_res.data:
        doc_data = doctor_res.data[0]
        print(f"✅ Found Doctor: {doc_data['name']} ({doc_data.get('specialization', 'N/A')})")
    else:
        print(f"⚠️ Warning: Doctor {DOCTOR_ID} not found in DB.")
        doc_data = {"name": "Dr. AyurEze Specialist", "experience_years": 10}

    # Retrieve Patient
    patient = await db_manager.get_patient_profile(PATIENT_ID)
    if not patient:
         print(f"❌ Error: Patient {PATIENT_ID} not found. Using fallback.")
         patient = {"name": "Subash", "email": "d.subash2710@gmail.com", "phone": "+91 91763 68156"}
    else:
         print(f"✅ Found Patient: {patient['name']} ({patient.get('phone', 'N/A')})")

    # 3. Create Real Doctor Prescription Data
    print(f"\nStep 2: Preparing Authentic Ayurvedic Prescription for {patient['name']}...")
    
    # High-quality medical data for Amavata (RA)
    presc_request = PrescriptionRequest(
        patient=PatientInfo(
            name=patient['name'],
            contact=patient.get('phone') or patient.get('email'),
            age=30,
            sex="Male",
            patient_id=PATIENT_ID
        ),
        doctor=DoctorInfo(
            name=doc_data['name'],
            regn_no="AYU-7712",
            contact="+91 89689 68156"
        ),
        diagnosis="Amavata (Rheumatoid Arthritis) - Samana Vata Vitiation",
        prescriptions=[
            PrescriptionItem(
                medicine="Amavatari Rasa",
                dose="250mg",
                quantity=20,
                schedule="Twice daily",
                timing="After Food",
                instructions="Helps digest Aama (toxins) and reduces joint pain.",
                duration="10 days"
            ),
            PrescriptionItem(
                medicine="Yograj Guggulu",
                dose="500mg",
                quantity=40,
                schedule="Twice daily",
                timing="After Food",
                instructions="Specific for Vata dominance in joints.",
                duration="20 days"
            )
        ],
        doctor_notes="Strictly avoid fermented foods and excessive salt. Practice regular Sukshma Vyayama (light joint movements)."
    )

    # 4. Execute Full Automation Pipeline
    print(f"\nStep 3: Executing Full Automation Pipeline...")
    result = await automated_prescription_service.process_prescription(
        prescription_data=presc_request,
        doctor_id=DOCTOR_ID,
        patient_id=PATIENT_ID
    )

    # 5. Handle Results
    if result["success"]:
        print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"   -------------------------------------------------")
        print(f"   Prescription ID  : {result['prescription_id']}")
        print(f"   Shopify Order    : {result['shopify_order']['draft_order_id']}")
        print(f"   Invoice URL      : {result['shopify_order']['invoice_url']}")
        print(f"   EHR Cloud Store  : {result['pdf_url']}")
        print(f"   -------------------------------------------------")
        
        with open("PRESCRIPTION_COMPLETE_LOG.json", "w") as f:
            json.dump(result, f, indent=4)
        print(f"\nReport logged to: PRESCRIPTION_COMPLETE_LOG.json")
    else:
        print(f"\n❌ PIPELINE PARTIAL FAILURE:")
        for err in result.get("errors", []):
            print(f"   - {err}")

    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(complete_flow())
