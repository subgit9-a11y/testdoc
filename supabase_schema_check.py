
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def check():
    c = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    res = c.table("patient_profiles").select("*").limit(1).execute()
    if res.data:
        print(f"SUPABASE COLUMNS: {list(res.data[0].keys())}")
    else:
        print("Empty Table")

if __name__ == "__main__":
    asyncio.run(check())
