import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def check_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("Missing Supabase credentials")
        return

    supabase = create_client(url, key)
    
    print("--- Searching for Doctors ---")
    doctors = supabase.table("doctor_profiles").select("*").limit(5).execute()
    if doctors.data:
        for d in doctors.data:
            print(f"Doctor ID: {d.get('doctor_id')}, Name: {d.get('name')}")
    else:
        print("No doctors found in Supabase")

    print("\n--- Searching for Patients ---")
    patients = supabase.table("patient_profiles").select("*").limit(5).execute()
    if patients.data:
        for p in patients.data:
            print(f"Patient ID: {p.get('patient_id')}, Name: {p.get('name')}, Code: {p.get('patient_code')}")
    else:
        print("No patients found in Supabase")

if __name__ == "__main__":
    asyncio.run(check_data())
