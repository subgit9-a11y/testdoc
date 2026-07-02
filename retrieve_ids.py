
import asyncio
import os
from dotenv import load_dotenv
from app.database import db_manager

load_dotenv()

async def run():
    print("Fetching real IDs data...")
    try:
        doctors = db_manager.client.table('doctors').select('*').limit(3).execute()
        print("\nDoctors:")
        for doc in doctors.data:
            print(f"ID: {doc.get('doctor_id')}, Name: {doc.get('name')}")
            
        patients = db_manager.client.table('patient_profiles').select('*').limit(3).execute()
        print("\nPatients:")
        for pat in patients.data:
            print(f"ID: {pat.get('patient_id')}, Name: {pat.get('name')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
