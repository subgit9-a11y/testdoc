
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

async def sync_real_patients():
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
    print("SYNCING VERIFIED CLINICAL PATIENTS: Legacy DB -> Astra AI")
    print("="*80)
    
    try:
        mysql_conn = pymysql.connect( host=host, user=user, password=password, database=dbname, port=port, cursorclass=pymysql.cursors.DictCursor )
        
        with mysql_conn.cursor() as cursor:
            # 1. First, check if there's a record for Subash to keep
            cursor.execute("SELECT * FROM users WHERE name LIKE '%Subash%' LIMIT 5")
            subash_users = cursor.fetchall()
            print(f"📦 Found {len(subash_users)} Subash candidates in [users] table.")
            
            # 2. Check the real patients table
            cursor.execute("SELECT * FROM users WHERE doctor_id IS NULL AND id > 10")
            verified_patients = cursor.fetchall()
            print(f"📦 Found {len(verified_patients)} clinical patient records.")

            for i, pt in enumerate(verified_patients, 1):
                name = str(pt.get('name') or "Clinical Patient")
                
                # We use the existing legacy id to maintain history
                l_id = str(pt.get('id', i))
                
                pt_data = {
                    "patient_id": f"PAT-REAL-{l_id}",
                    "patient_code": f"P-{l_id}",
                    "name": name,
                    "phone": str(pt.get('phone') or pt.get('phone_no') or ""),
                    "email": str(pt.get('email') or ""),
                    "is_active": True
                }
                
                try:
                    supabase.table("patient_profiles").upsert(pt_data).execute()
                    print(f"   ✅ [P-{l_id}] Synced: {name}")
                except Exception as se:
                    print(f"   ❌ Supabase Sync Error (P-{l_id}): {se}")

        print("\n" + "="*80)
        print("VERIFIED REAL PATIENT SYNC COMPLETE!")
        print("="*80)

    except Exception as e:
        print(f"\nDatabase Connection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(sync_real_patients())
