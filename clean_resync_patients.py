
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

async def clean_and_resync_patients():
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
    print("RE-CLEANING & SYNCING ONLY REAL PATIENTS FROM MySQL [patients] TABLE")
    print("="*80)
    
    try:
        # 1. Clean current wrong data from Supabase
        print("\n🧹 Cleaning current patient registry in Supabase...")
        try:
            # We delete everything from patient_profiles to start fresh
            # Note: In production Supabase might need specific filter for delete All or truncate
            # We'll try to find any one to delete
            supabase.table("patient_profiles").delete().neq("is_active", "false").execute()
            print("   ✅ Cleaned patient registry.")
        except Exception as ce:
            print(f"   ⚠️ Could not clean Supabase: {ce}")

        # 2. Sync from Legacy MySQL ONLY the [patients] table
        mysql_conn = pymysql.connect(
            host=host, user=user, password=password, database=dbname, port=port,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=15
        )
        
        with mysql_conn.cursor() as cursor:
            # Check patients table
            print("\n📦 Fetching verified patient records from [patients] table...")
            cursor.execute("SELECT * FROM patients")
            real_pts = cursor.fetchall()
            print(f"   Found {len(real_pts)} verified patients.")

            for i, p in enumerate(real_pts, 1):
                # Legacy patients often have user_id links
                full_name = p.get('name') or f"Patient {p.get('id')}"
                
                pt_data = {
                    "patient_id": str(p.get('id')), # Use their legacy ID
                    "patient_code": f"PAT-{p.get('id') or i}",
                    "name": str(full_name),
                    "phone": str(p.get('phone') or ""),
                    "email": str(p.get('email') or ""),
                    "location": str(p.get('address') or ""),
                    "is_active": True
                }
                
                try:
                    supabase.table("patient_profiles").upsert(pt_data).execute()
                    print(f"   ✅ [PAT-{pt_data['patient_id']}] Synced: {pt_data['name']}")
                except Exception as se:
                    print(f"   ❌ Sync Error (PAT-{p.get('id')}): {se}")

        print("\n" + "="*80)
        print("VERIFIED PATIENT SYNC COMPLETE!")
        print("="*80)

    except Exception as e:
        print(f"\nConnection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(clean_and_resync_patients())
