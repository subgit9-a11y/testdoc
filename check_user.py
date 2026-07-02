import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())
load_dotenv()

async def check():
    from app.database import db_manager
    print(f"INFO: Supabase Connected: {db_manager.is_connected()}")
    
    email = "d.subash2710@gmail.com"
    print(f"INFO: Checking for user with email: {email}")
    
    # Search for patients by name or email (search_patients uses name.ilike, etc.)
    patients = await db_manager.search_patients("Subash")
    print(f"SUCCESS: Found patients count: {len(patients)}")
    if patients:
        for p in patients:
            print(f"Patient ID: {p.get('patient_id')}, Name: {p.get('name')}, Email: {p.get('email')}")
            
    # Search in astra_users if possible?
    # db_manager doesn't have search_users, but it has upsert_user that matches by id.
    # We'll just run the scenario script which will upsert the user anyway.

if __name__ == "__main__":
    asyncio.run(check())
