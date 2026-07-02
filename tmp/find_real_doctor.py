import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Windows UTF-8 fix
if sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

load_dotenv(override=True)

def find_doctor():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("Missing credentials")
        return

    supabase = create_client(url, key)
    
    print(f"Connecting to {url}...")
    try:
        # Check doctor_profiles
        res = supabase.table("doctor_profiles").select("*").limit(3).execute()
        if res.data:
            print(f"Found {len(res.data)} doctors:")
            for d in res.data:
                print(f"ID: {d.get('doctor_id')}, Name: {d.get('name')}, Email: {d.get('email')}")
        else:
            print("No doctors found in 'doctor_profiles'")
            
        # Check patient_profiles
        res = supabase.table("patient_profiles").select("*").limit(3).execute()
        if res.data:
            print(f"\nFound {len(res.data)} patients:")
            for p in res.data:
                print(f"ID: {p.get('patient_id')}, Name: {p.get('name')}, Code: {p.get('patient_code')}")
        else:
            print("No patients found in 'patient_profiles'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_doctor()
