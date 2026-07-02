import os
from app.ayureze_prescription_template import generate_ayureze_prescription_pdf

class MockProfile:
    def __init__(self, name, reg=""):
        self.name = name
        self.registration_no = reg

class MockPatient:
    def __init__(self, name, age, gender, contact):
        self.name = name
        self.age = age
        self.gender = gender
        self.contact_number = contact

class MockPrescription:
    def __init__(self):
        self.patient = MockPatient("Subhash's Brother", "28", "Male", "+91-9876543210")
        self.doctor_profile = MockProfile("Dr. AI Specialist", "REG-12345")
        self.diagnosis = "Mild Stress and Vata Imbalance"
        self.consultation_id = "CONS-MOCK"
        self.medicines = [
            {"product_name": "Triphala Churnam", "dosage": "1 tsp", "time": "After Food"},
            {"product_name": "Ashwagandha", "dosage": "1-0-1", "time": "Before Food"}
        ]
        self.external_therapy = "Abhyanga with sesame oil."

def test():
    print("Starting Mock Prescription Generation (On Base Image)...")
    p = MockPrescription()
    try:
        pdf_data = generate_ayureze_prescription_pdf(p)
        with open("mock_verified_on_base.pdf", "wb") as f:
            f.write(pdf_data)
        print(f"✅ SUCCESS: PDF generated on base template. Size: {len(pdf_data)} bytes.")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test()
