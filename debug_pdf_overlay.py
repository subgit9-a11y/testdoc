import os
import asyncio
from dotenv import load_dotenv
from app.ayureze_prescription_template import generate_ayureze_prescription_pdf
from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

async def debug_pdf_rendering():
    load_dotenv()
    print("Debugging PDF Overlay Rendering...")
    
    # Check if base image exists
    # Using the real relative path from app/ayureze_prescription_template.py
    base_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "assets", "base_prescription.png")
    if os.path.exists(base_img_path):
        print(f"Base image found at: {base_img_path}")
    else:
        print(f"Base image MISSING: {base_img_path}")
        # Try a Different Path
        base_img_path = os.path.abspath("app/assets/base_prescription.png")
        print(f"Alternative Check: {base_img_path}")
        if not os.path.exists(base_img_path):
            print("ERROR: Background prescription image NOT FOUND.")
            return

    # Mock Data
    class MockPatient:
        def __init__(self, name, age, contact): self.name, self.age, self.contact = name, age, contact
    class MockDoctor:
        def __init__(self, name, reg): self.name, self.regn_no = name, reg
        
    patient = MockPatient("Subhash (DEBUG)", 28, "6380167373")
    doctor = MockDoctor("Dr. Astra AI", "AY12345/ASTR")
    
    # We need the real Pydantic models for the function call
    from app.shopify_models import PrescriptionItem
    
    items = [
        PrescriptionItem(medicine="Triphala Churna", dose="1 tbsp", schedule="1-0-1", timing="After meals", duration="15 days", quantity=1, instructions="Warm water")
    ]
    
    # Re-importing to ensure correct schema
    from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo
    
    prescription = PrescriptionRequest(
        patient=PatientInfo(name=patient.name, contact=patient.contact, age=patient.age, gender="Male"),
        doctor=DoctorInfo(name=doctor.name, regn_no=doctor.regn_no, contact="+91 98765 43210"),
        prescriptions=items,
        diagnosis="Debug Overlay Check",
        doctor_notes="Testing background image alignment."
    )
    
    try:
        # Generate PDF
        pdf_data = generate_ayureze_prescription_pdf(prescription)
        
        # Save to local file for user to inspect
        file_name = "DEBUG_Prescription_Overlay.pdf"
        with open(file_name, "wb") as f:
            f.write(pdf_data)
        
        print(f"Success: {file_name} has been generated.")
        print(f"Absolute Path: {os.path.abspath(file_name)}")
    except Exception as e:
        print(f"Rendering Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pdf_rendering())
