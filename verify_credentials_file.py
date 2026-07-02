
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env_var(var_name, required=True):
    value = os.getenv(var_name)
    if value and value.strip():
        return f"✅ {var_name}: PRESENT"
    else:
        status = "MISSING (REQUIRED)" if required else "MISSING (OPTIONAL)"
        icon = "❌" if required else "⚠️"
        return f"{icon} {var_name}: {status}"

def verify_all_credentials():
    report = []
    report.append("🔍 Verifying Astra Backend Credentials...\n")
    
    report.append("--- Core Infrastructure ---")
    report.append(check_env_var("DATABASE_URL"))
    report.append(check_env_var("SUPABASE_URL"))
    report.append(check_env_var("SUPABASE_ANON_KEY"))
    
    report.append("\n--- AI Brain (Astra) ---")
    report.append(check_env_var("ASTRA_API_ENDPOINT", required=False))
    
    report.append("\n--- WhatsApp Integration (Custom) ---")
    report.append(check_env_var("CUSTOM_WA_API_BASE_URL"))
    report.append(check_env_var("CUSTOM_WA_BEARER_TOKEN"))
    report.append(check_env_var("CUSTOM_WA_VENDOR_UID"))
    report.append(check_env_var("CUSTOM_WA_FROM_PHONE_ID", required=False))
    
    report.append("\n--- Decentralized Storage (Storj) ---")
    report.append(check_env_var("STORJ_ACCESS_KEY"))
    report.append(check_env_var("STORJ_SECRET_KEY"))
    report.append(check_env_var("STORJ_ENDPOINT", required=False))
    
    report.append("\n--- E-Commerce (Shopify) ---")
    report.append(check_env_var("SHOPIFY_SHOP_URL"))
    report.append(check_env_var("SHOPIFY_ACCESS_TOKEN"))
    report.append(check_env_var("SHOPIFY_API_VERSION"))
    
    report.append("\n--- Authentication (Firebase) ---")
    report.append(check_env_var("FIREBASE_CREDENTIAL_PATH", required=False))
    
    with open("credential_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    verify_all_credentials()
