
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
        res = supabase.table("doctor_profiles").select("*").execute()
        print("\n--- DOCTOR PROFILES ---")
        for d in res.data:
            print(f"ID: {d.get('doctor_id')}, Name: {d.get('name')}")
    except:
        print("Table 'doctor_profiles' error.")

    try:
        res = supabase.table("doctors").select("*").execute()
        print("\n--- DOCTORS ---")
        for d in res.data:
            print(f"ID: {d.get('doctor_id')}, Name: {d.get('name')}")
    except:
        print("Table 'doctors' error.")

if __name__ == "__main__":
    asyncio.run(list_profiles())
