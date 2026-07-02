import os
from dotenv import load_dotenv
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.ERROR) # Only show errors
load_dotenv(override=True)

# Set encoding to UTF-8 for this script output (Windows terminal fix)
if sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Add current directory to path
sys.path.append(os.getcwd())

from app.shopify_client import shopify_client
from app.shopify_models import PrescriptionRequest, PatientInfo, DoctorInfo, PrescriptionItem

def debug_prescription_flow():
    print("\n" + "="*50)
    print("SHOPIFY PRESCRIPTION DEBUGGER (NO EMOJIS)")
    print("="*50)

    # 1. Test Product Search
    medicines_to_test = [
        "Aadarisahacharadi Kashayam", 
        "Sahacharadi Kashayam", 
        "Dhanwantharam Thailam", 
        "Triphala Churna"
    ]
    
    print("\n[PHASE 1]: Testing Product Search & Mapping")
    found_meds = []
    for med in medicines_to_test:
        print(f"Searching for: {med}...")
        try:
            result = shopify_client.search_product(med)
            if result.get("is_available"):
                print(f"   [SUCCESS] FOUND: {result.get('shopify_product_title')} (ID: {result.get('shopify_variant_id')})")
                found_meds.append(med)
            else:
                print(f"   [FAIL] NOT FOUND: {med}")
        except Exception as e:
            print(f"   [ERROR] Search failed: {e}")

    # 2. Test Draft Order Creation
    print("\n[PHASE 2]: Testing Draft Order Creation")
    
    # Create request with at least one found med
    if not found_meds:
        print("   [CRITICAL] No medicines found in shopify. Cannot test order creation.")
        return

    test_med = found_meds[0]
            
    presc_request = PrescriptionRequest(
        patient=PatientInfo(name="Debug Patient", contact="debug@example.com", age=25),
        doctor=DoctorInfo(name="Debug Doctor", regn_no="DEBUG-001"),
        diagnosis="Debug Diagnosis",
        prescriptions=[
            PrescriptionItem(
                medicine=test_med, dose="5ml", quantity=1,
                schedule="Twice daily", timing="Morning/Night", duration="5 days"
            )
        ]
    )

    try:
        print(f"Creating draft order for medicine: {test_med}...")
        order_res = shopify_client.create_draft_order(presc_request)
        print(f"   [SUCCESS] Draft Order Created")
        print(f"   - Order ID: {order_res.draft_order_id}")
        print(f"   - Invoice URL: {order_res.invoice_url}")
        print(f"   - Unmapped: {order_res.unmapped_medicines}")
    except Exception as e:
        print(f"   [FAIL] Order creation failed: {e}")

if __name__ == "__main__":
    debug_prescription_flow()
