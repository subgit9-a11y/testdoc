
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env_var(var_name, required=True):
    value = os.getenv(var_name)
    if value and value.strip():
        # Mask the value for security, show only first 4 chars if long enough
        masked_value = value[:4] + "****" if len(value) > 4 else "****"
        print(f"✅ {var_name}: PRESENT")
        return True
    else:
        status = "MISSING (REQUIRED)" if required else "MISSING (OPTIONAL)"
        icon = "❌" if required else "⚠️"
        print(f"{icon} {var_name}: {status}")
        return False

def verify_all_credentials():
    print("\n🔍 Verifying Astra Backend Credentials...\n")
    
    all_good = True
    
    print("--- Core Infrastructure ---")
    if not check_env_var("DATABASE_URL"): all_good = False
    if not check_env_var("SUPABASE_URL"): all_good = False
    if not check_env_var("SUPABASE_ANON_KEY"): all_good = False
    
    print("\n--- AI Brain (Astra) ---")
    # This might not be an env var if hardcoded in astra_client.py, but good to check if override exists
    check_env_var("ASTRA_API_ENDPOINT", required=False) 
    
    print("\n--- WhatsApp Integration (Custom) ---")
    if not check_env_var("CUSTOM_WA_API_BASE_URL"): all_good = False
    if not check_env_var("CUSTOM_WA_BEARER_TOKEN"): all_good = False
    if not check_env_var("CUSTOM_WA_VENDOR_UID"): all_good = False
    check_env_var("CUSTOM_WA_FROM_PHONE_ID", required=False)
    
    print("\n--- Decentralized Storage (Storj) ---")
    if not check_env_var("STORJ_ACCESS_KEY"): all_good = False
    if not check_env_var("STORJ_SECRET_KEY"): all_good = False
    check_env_var("STORJ_ENDPOINT", required=False)
    
    print("\n--- E-Commerce (Shopify) ---")
    if not check_env_var("SHOPIFY_SHOP_URL"): all_good = False
    if not check_env_var("SHOPIFY_ACCESS_TOKEN"): all_good = False
    if not check_env_var("SHOPIFY_API_VERSION"): all_good = False
    
    print("\n--- Authentication (Firebase) ---")
    check_env_var("FIREBASE_CREDENTIAL_PATH", required=False)
    
    print("\n" + "="*40)
    if all_good:
        print("🎉 ALL REQUIRED CREDENTIALS DETECTED!")
        print("Ready for deployment.")
    else:
        print("🚫 MISSING CREDENTIALS DETECTED.")
        print("Please check your .env file and fill in the missing values.")
    print("="*40 + "\n")

if __name__ == "__main__":
    verify_all_credentials()
