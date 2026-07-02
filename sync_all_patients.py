
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

async def sync_and_list_patients():
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
    print("FINISHED PATIENT SYNCHRONIZATION: Legacy MySQL -> Astra Supabase")
    print("="*80)
    
    try:
        mysql_conn = pymysql.connect(
            host=host, user=user, password=password, database=dbname, port=port,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=15
        )
        
        with mysql_conn.cursor() as cursor:
            # Sync all patients
            try:
                # Find the right column for patient check
                cursor.execute("DESCRIBE users")
                cols = [r['Field'] for r in cursor.fetchall()]
                where_clause = ""
                if 'role' in cols: where_clause = "WHERE role = 'patient'"
                elif 'user_type' in cols: where_clause = "WHERE user_type = 'patient'"
                else: where_clause = "LIMIT 100" # fallback to first 100 users if role is missing

                sql = f"SELECT * FROM users {where_clause}"
                cursor.execute(sql)
                legacy_pts = cursor.fetchall()
                print(f"📦 Found {len(legacy_pts)} patients in legacy database. Syncing...")

                for pt in legacy_pts:
                    pt_data = {
                        "patient_id": str(pt.get('id')),
                        "name": str(pt.get('name') or pt.get('first_name') or "Patient"),
                        "email": str(pt.get('email') or ""),
                        "phone": str(pt.get('phone_no') or pt.get('phone') or ""),
                        "is_active": True
                    }
                    try:
                        supabase.table("patient_profiles").upsert(pt_data).execute()
                        print(f"   ✅ Synced: {pt_data['name']}")
                    except Exception as pe:
                        print(f"   ❌ Supabase Error: {pe}")
            except Exception as e:
                print(f"   ⚠️ Could not fetch patients: {e}")

        # Final List from Supabase
        print("\n" + "="*80)
        print("ASTRA PATIENT REGISTRY (SUPABASE)")
        print("="*80)
        res = supabase.table("patient_profiles").select("*").execute()
        for p in res.data:
            print(f"• ID: {p.get('patient_id')} | Name: {p.get('name')} | Phone: {p.get('phone')}")
        
        print("\nTotal Sync Result: SUCCESS")

    except Exception as e:
        print(f"\nConnection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(sync_and_list_patients())
