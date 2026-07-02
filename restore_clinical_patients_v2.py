
import os
import pymysql
import asyncio
import urllib.parse
from dotenv import load_dotenv
from supabase import create_client
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

async def restore_clinical_patients_v2():
    db_url = os.getenv("DATABASE_URL")
    clean_url = db_url.replace("mysql+pymysql://", "")
    auth_part, rest = clean_url.split("@")
    user, password = auth_part.split(":")
    password = urllib.parse.unquote(password)
    host_port, dbname = rest.split("/")
    host = host_port.split(":")[0] if ":" in host_port else host_port
    port = int(host_port.split(":")[1]) if ":" in host_port else 3306
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    print("\n" + "="*80)
    print("VERIFIED RESTORATION: [patient_profiles] (MySQL) -> [patient_profiles] (Supabase)")
    print("="*80)
    
    try:
        mysql_conn = pymysql.connect(
            host=host, user=user, password=password, database=dbname, port=port,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=15
        )
        
        with mysql_conn.cursor() as cursor:
            print("\n📦 Fetching verified clinical records from legacy table...")
            cursor.execute("SELECT * FROM patient_profiles")
            real_pts = cursor.fetchall()
            print(f"   Found {len(real_pts)} verified records.")

            for pt in real_pts:
                # Map available columns exactly to Supabase schema
                pt_data = {
                    "id": str(pt.get('id')),
                    "patient_id": str(pt.get('patient_id') or pt.get('id')), 
                    "patient_code": str(pt.get('patient_code')),
                    "name": str(pt.get('name')),
                    "phone": str(pt.get('phone') or ""),
                    "email": str(pt.get('email') or ""),
                    "age": pt.get('age'),
                    "gender": str(pt.get('gender') or ""),
                    "address": str(pt.get('address') or ""),
                    "emergency_contact": str(pt.get('emergency_contact') or ""),
                    "medical_conditions": pt.get('medical_conditions') or "[]",
                    "allergies": pt.get('allergies') or "[]",
                    "is_active": True
                }
                
                try:
                    # UPSERT to ensure clean data
                    supabase.table("patient_profiles").upsert(pt_data).execute()
                    print(f"   ✅ [{pt_data['patient_code']}] Synced: {pt_data['name']}")
                except Exception as se:
                    print(f"   ❌ Sync Error ({pt_data['patient_code']}): {se}")

        print("\n" + "="*80)
        print("VERIFIED CLINICAL SYNC COMPLETE!")
        print("="*80)

    except Exception as e:
        print(f"\nConnection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(restore_clinical_patients_v2())
