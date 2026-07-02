import os
from dotenv import load_dotenv
import logging
import sys

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)

# Add current directory to path
sys.path.append(os.getcwd())

from app.shopify_client import shopify_client
from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

def debug_prescription_flow():
    print("\n" + "="*50)
    print("SHOPIFY PRESCRIPTION DEBUGGER")
    print("="*50)

    # 1. Test Product Search
    medicines_to_test = [
        "Aadarisahacharadi Kashayam", 
        "Sahacharadi Kashayam", 
        "Dhanwantharam Thailam", 
        "Triphala Churna"
    ]
    
    print("\n[PHASE 1]: Testing Product Search & Mapping")
    for med in medicines_to_test:
        print(f"Searching for: {med}...")
        result = shopify_client.search_product(med)
        if result.get("is_available"):
            print(f"   ✅ FOUND: {result.get('shopify_product_title')} (ID: {result.get('shopify_variant_id')})")
        else:
            print(f"   ❌ NOT FOUND: {med}")

    # 2. Test Draft Order Creation
    print("\n[PHASE 2]: Testing Draft Order Creation")
    
    # Create a mock prescription request
    # Use the first found medicine if any, else use a dummy one
    test_med = "Sahacharadi Kashayam" # Default
    for med in medicines_to_test:
        if shopify_client.search_product(med).get("is_available"):
            test_med = med
            break
            
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name="Debug Patient", contact="debug@example.com", age=25),
        doctor=DoctorInfo(name="Debug Doctor", regn_no="DEBUG-001"),
        diagnosis="Debug Diagnosis",
        prescriptions=[
            PrescriptionItem(
                medicine=test_med,
                dose="5ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="5 days"
            )
        ]
    )

    try:
        print(f"Creating draft order for medicine: {test_med}...")
        order_res = shopify_client.create_draft_order(presc_request)
        print(f"   ✅ SUCCESS: Draft Order Created")
        print(f"   - Order ID: {order_res.draft_order_id}")
        print(f"   - Invoice URL: {order_res.invoice_url}")
        print(f"   - Unmapped: {order_res.unmapped_medicines}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    debug_prescription_flow()
