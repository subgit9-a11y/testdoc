import os
import asyncio
from dotenv import load_dotenv

async def main():
    load_dotenv()
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    client = create_client(url, key)
    
    # List doctors
    res = client.table("doctors").select("*").execute()
    print(f"Doctors: {res.data}")
    
    # List patient profiles
    res = client.table("patient_profiles").select("*").limit(1).execute()
    print(f"Patients: {res.data}")

if __name__ == "__main__":
    asyncio.run(main())
