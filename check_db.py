import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

async def check_schema():
    from app.database import db_manager
    if not db_manager.client:
        print("Supabase client not initialized")
        return
    
    tables = ["astra_users", "patient_profiles", "consultations", "prescription_records", "astra_chat_history"]
    
    print("Database Schema Check:")
    for table in tables:
        try:
            print(f"\nTable: {table}")
            res = db_manager.client.table(table).select("*").limit(1).execute()
            if res.data:
                print(f"  Columns: {list(res.data[0].keys())}")
            else:
                print("  No data found to check columns.")
        except Exception as e:
            print(f"  Error accessing table: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
