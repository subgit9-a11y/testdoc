
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

async def list_roster():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    print("\n" + "="*80)
    print("ASTRA AI ENGINE: LIVE ROSTER DATA (Supabase)")
    print("="*80)

    # 1. Doctors
    try:
        res_d = supabase.table("doctors").select("*").execute()
        print(f"\n👨‍⚕️ DOCTORS ({len(res_d.data)} Records):")
        print("-" * 50)
        for d in res_d.data:
            name = d.get('name') or "Unknown"
            spec = d.get('specialization') or "GP"
            doc_id = d.get('doctor_id') or "N/A"
            print(f"[{doc_id}] {name} - {spec}")
    except Exception as de:
        print(f"⚠️ Error fetching doctors: {de}")

    # 2. Patients
    try:
        res_p = supabase.table("patient_profiles").select("*").execute()
        print(f"\n👤 PATIENTS ({len(res_p.data)} Records):")
        print("-" * 50)
        for p in res_p.data:
            name = p.get('name') or "Unknown"
            phone = p.get('phone') or "N/A"
            email = p.get('email') or "N/A"
            print(f"• {name} (Phone: {phone}, Email: {email})")
    except Exception as pe:
        print(f"⚠️ Error fetching patients: {pe}")

    print("\n" + "="*80)
    print("ROSTER DISPLAY COMPLETE!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(list_roster())
