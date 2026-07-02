import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(supabase_url, supabase_key)

mock_patient = {
    "patient_id": "PAT-MOCK-123",
    "patient_code": "P-MOCK",
    "name": "Mock Test Patient",
    "email": "mock@ayureze.in",
    "phone": "+919876543210",
    "is_active": True
}

try:
    # Check if exists
    res = supabase.table("patient_profiles").select("*").eq("patient_id", "PAT-MOCK-123").execute()
    if not res.data:
        print("Inserting mock patient...")
        supabase.table("patient_profiles").insert(mock_patient).execute()
        print("Done!")
    else:
        print("Mock patient already exists.")
except Exception as e:
    print(f"Error: {e}")
