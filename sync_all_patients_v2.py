
import os
import pymysql
import asyncio
import urllib.parse
import uuid
from dotenv import load_dotenv
from supabase import create_client
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

async def sync_and_list_patients_v2():
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
    print("ENHANCED PATIENT SYNC: Legacy MySQL -> Supabase (with Patient Codes)")
    print("="*80)
    
    try:
        mysql_conn = pymysql.connect(
            host=host, user=user, password=password, database=dbname, port=port,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=15
        )
        
        with mysql_conn.cursor() as cursor:
            # Sync all patients
            try:
                # Find available columns
                cursor.execute("DESCRIBE users")
                cols = [r['Field'] for r in cursor.fetchall()]
                where_clause = ""
                if 'role' in cols: where_clause = "WHERE role = 'patient'"
                elif 'user_type' in cols: where_clause = "WHERE user_type = 'patient'"
                else: where_clause = "" # sync all if no role found

                sql = f"SELECT * FROM users {where_clause} LIMIT 100"
                cursor.execute(sql)
                legacy_pts = cursor.fetchall()
                print(f"📦 Found {len(legacy_pts)} patient records in legacy DB.")

                for i, pt in enumerate(legacy_pts, 1):
                    # Generate data
                    l_id = pt.get('id')
                    name = str(pt.get('name') or pt.get('username') or "Patient")
                    email = str(pt.get('email') or "")
                    phone = str(pt.get('phone_no') or pt.get('phone') or "")
                    
                    # Create the record for Supabase
                    pt_data = {
                        "patient_id": str(uuid.uuid4()), # New internal UUID
                        "patient_code": f"PAT-{l_id or i}", # Required by schema
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "is_active": True
                    }
                    
                    try:
                        # Attempt to upsert based on name/email/phone match or just insert
                        # We try to avoid duplicates if possible, but for first sync we just insert
                        supabase.table("patient_profiles").insert(pt_data).execute()
                        print(f"   ✅ [PAT-{l_id}] Synced: {name}")
                    except Exception as pe:
                        if "already exists" in str(pe) or "Duplicate" in str(pe):
                            print(f"   ℹ️ Skipped (Existing): {name}")
                        else:
                            print(f"   ❌ Supabase Error (PAT-{l_id}): {pe}")

            except Exception as e:
                print(f"   ⚠️ Sync Operation Error: {e}")

        # --- FINAL DISPLAY ---
        print("\n" + "="*80)
        print("ASTRA AI ENGINE: COMPLETE PATIENT REGISTRY (LIVE)")
        print("="*80)
        res = supabase.table("patient_profiles").select("*").execute()
        for p in res.data:
            code = p.get('patient_code', 'N/A')
            name = p.get('name', 'N/A')
            phone = p.get('phone', 'N/A')
            print(f"[{code}] {name} - {phone}")
        
        print("\n" + "="*80)
        print("SYNCHRONIZATION & LISTING COMPLETE!")
        print("="*80)

    except Exception as e:
        print(f"\nConnection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(sync_and_list_patients_v2())
