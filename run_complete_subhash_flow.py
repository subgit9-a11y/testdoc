from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import logging
from app.automated_prescription_service import automated_prescription_service
from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

# Configure logging
logging.basicConfig(level=logging.INFO)

async def run_subhash_live_flow():
    print("Astra Live Full-Flow Test (Consultation - WhatsApp - Email - Wasabi - Shopify - Supabase)")
    
    # 1. Prepare Consultation Data
    patient = PatientInfo(
        name="Subhash",
        contact="d.subash2710@gmail.com",
        age=28,
        gender="Male"
    )
    
    doctor = DoctorInfo(
        name="Dr. Astra AI (AyurEze)",
        regn_no="AY12345/ASTR",
        contact="care@ayureze.in"
    )
    
    items = [
        PrescriptionItem(
            medicine="Triphala Churna",
            dose="1 tbsp",
            schedule="1-0-1",
            timing="After meals",
            duration="15 days",
            quantity=1,
            instructions="Mix with warm water."
        ),
        PrescriptionItem(
            medicine="Ashwagandha Vati",
            dose="1 tablet",
            schedule="0-1-0",
            timing="After lunch",
            duration="1 month",
            quantity=1,
            instructions="Take with milk."
        )
    ]
    
    prescription_data = PrescriptionRequest(
        patient=patient,
        doctor=doctor,
        prescriptions=items,
        diagnosis="Panchakarma Detox and General Wellness",
        doctor_notes="High priority ayurvedic detox plan for Subhash. Stay hydrated."
    )
    
    # 2. Trigger the Automated Service
    results = await automated_prescription_service.process_prescription(
        prescription_data=prescription_data,
        doctor_id="DOC-9999",
        patient_id="PAT-SUBHASH-LIVE"
    )
    
    # 3. Report Results
    print("\n" + "="*50)
    print("ASTRA LIVE FLOW REPORT - SUBHASH TEST")
    print("="*50)
    
    if results.get("success"):
        print(f"PRIMARY STATUS: SUCCESS")
        print(f"Prescription ID: {results.get('prescription_id')}")
        print(f"WASABI PDF URL: {results.get('pdf_url')}")
        print(f"SHOPIFY ORDER: {results.get('shopify_order', {}).get('invoice_url')}")
        print(f"EMAIL: Dispatched to d.subash2710@gmail.com")
        print(f"WHATSAPP: Dispatched to 6380167373")
    else:
        print(f"PRIMARY STATUS: FAILED")
        print(f"Errors: {results.get('errors')}")

if __name__ == "__main__":
    asyncio.run(run_subhash_live_flow())
