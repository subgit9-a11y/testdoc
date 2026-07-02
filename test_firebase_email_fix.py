import os
import asyncio
import logging
from dotenv import load_dotenv
from app.firebase_email_service import FirebaseEmailService

# Set up logging to console
logging.basicConfig(level=logging.INFO)

async def test_firebase_email():
    load_dotenv()
    print("Testing Firebase Email Service...")
    
    # Instantiate manually to see logs
    service = FirebaseEmailService()
    print(f"Firebase Initialized: {service.firebase_initialized}")
    
    # Test send_custom_email (used by catchy prescription)
    print("Sending custom email...")
    result = await service.send_custom_email(
        to_email="no-reply@ayureze.in",
        subject="Test Custom Email",
        body="<h1>Test</h1><p>This is a test of the custom email method.</p>",
        pdf_attachment=b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj xref 0 4 0000000000 65535 f 0000000010 00000 n 0000000057 00000 n 0000000115 00000 n trailer<</Size 4/Root 1 0 R>>startxref 219 %%EOF",
        filename="test_custom.pdf"
    )
    
    if result.get("status") == "success":
        print("SUCCESS: Custom email sent.")
    else:
        print(f"FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_firebase_email())
