import asyncio
import logging
import os
from dotenv import load_dotenv

# Load env before importing app modules to ensure DB connections initialize
load_dotenv()

from app.doctors.doctor_service import doctor_service
from app.admin_db import admin_db
from sqlalchemy import text

# Set logger to INFO to see the internal logs of doctor_service
logging.basicConfig(level=logging.INFO)

async def run_test():
    print("==================================================")
    print("   DOCTOR ECOSYSTEM INTERLINK SYNC TEST           ")
    print("==================================================\n")
    
    legacy_id = None
    doctor_name = None
    
    # 1. Connect to MySQL and find a legacy doctor
    print("[1] Connecting to Legacy MySQL Database...")
    if not admin_db.engine:
        print("❌ MySQL Database not connected. Check DATABASE_URL in .env")
        return
        
    try:
        with admin_db.get_session() as session:
            result = session.execute(text("SELECT id, name FROM doctors LIMIT 1")).mappings().first()
            if result:
                legacy_id = str(result['id'])
                doctor_name = result['name']
                print(f"✅ Found Legacy Doctor in MySQL: ID={legacy_id} ({doctor_name})")
            else:
                print("❌ No doctors found in MySQL legacy database. Cannot test sync.")
                return
    except Exception as e:
        print(f"❌ Error querying MySQL: {e}")
        return

    print(f"\n[2] Simulating API Call to fetch Doctor 'DOC-{legacy_id}'...")
    print("    (This will trigger the Interlink Sync if missing in Supabase)")
    print("-" * 50)
    
    # 2. Run the get_doctor function
    res = await doctor_service.get_doctor(f"DOC-{legacy_id}")
    
    print("-" * 50)
    # 3. Analyze results
    if res.get("success"):
        print("\n✅ INTERLINK SYNC SUCCESSFUL!")
        print(f"The doctor profile was fetched successfully and is fully synced into Supabase.")
        print("Data returned by the API:")
        for k, v in res['data'].items():
            print(f"  > {k}: {v}")
    else:
        print(f"\n❌ SYNC FAILED: {res.get('error')}")

if __name__ == "__main__":
    asyncio.run(run_test())
