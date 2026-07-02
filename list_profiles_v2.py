
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def list_profiles():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # 1. Doctors
    try:
        # Check 'doctor_profiles'
        res = supabase.table("doctor_profiles").select("*").execute()
        print("\n--- DOCTOR PROFILES (Supabase) ---")
        for d in res.data:
            print(f"Doctor ID: {d.get('doctor_id')}")
            print(f"Name     : {d.get('name')}")
            print(f"Specialty: {d.get('specialization')}")
            print(f"Email    : {d.get('email')}")
            print("-" * 30)
    except Exception as e:
        print(f"Table 'doctor_profiles' not found or error: {e}")

    # 2. Check 'doctors' table (just in case)
    try:
        res = supabase.table("doctors").select("*").execute()
        print("\n--- DOCTORS (Supabase) ---")
        for d in res.data:
            print(f"ID: {d.get('doctor_id')}, Name: {d.get('name')}")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(list_profiles())
