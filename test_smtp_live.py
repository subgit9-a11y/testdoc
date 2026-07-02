import os
import asyncio
from dotenv import load_dotenv
from app.smtp_email_service import SmtpEmailService

async def test_smtp():
    load_dotenv()
    print("Triggering Official SMTP Test for AyurEze...")
    
    service = SmtpEmailService()
    
    # Mock PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj xref 0 4 0000000000 65535 f 0000000010 00000 n 0000000057 00000 n 0000000115 00000 n trailer<</Size 4/Root 1 0 R>>startxref 219 %%EOF"
    
    result = service.send_prescription_email(
        recipient_email="no-reply@ayureze.in",
        pdf_content=pdf_content,
        patient_name="Test Patient",
        doctor_name="Dr. Astra AI",
        prescription_id="TEST-SMTP-001"
    )
    
    if result.get("success"):
        print("SUCCESS: SMTP server accepted and delivered.")
    else:
        print(f"FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_smtp())
