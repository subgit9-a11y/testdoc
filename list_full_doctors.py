
import os
import asyncio
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def list_full_doctors():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # 1. Fetch from 'doctors' table
    res = supabase.table("doctors").select("*").execute()
    print("\n--- DOCTOR RECORDS (Supabase) ---")
    if res.data:
        for d in res.data:
            print(f"Doctor ID: {d.get('doctor_id')}")
            print(f"Name     : {d.get('name')}")
            print(f"Specialty: {d.get('specialization')}")
            print(f"Experience: {d.get('experience_years')} yrs")
            print(f"Fee      : INR {d.get('consultation_fee')}")
            print(f"Languages: {d.get('languages')}")
            print(f"Location : {d.get('address')}, {d.get('city')}, {d.get('state')}")
            print("-" * 30)
    else:
        print("No doctor records found in 'doctors' table.")

    # 2. Match with 'astra_users' for email/role
    res_users = supabase.table("astra_users").select("*").execute()
    print("\n--- DOCTOR USERS (astra_users) ---")
    if res_users.data:
        for u in res_users.data:
            metadata = u.get('metadata', {})
            # Some users might have role in metadata or a separate column
            if u.get('role') == 'doctor' or 'doctor' in str(metadata).lower() or 'doc' in u.get('id', '').lower():
                print(f"User ID  : {u.get('id')}")
                print(f"Email    : {u.get('email')}")
                print(f"Name     : {u.get('name')}")
                print(f"Verified : {u.get('email_verified')}")
                print("-" * 30)
    else:
        print("No users found.")

if __name__ == "__main__":
    asyncio.run(list_full_doctors())
