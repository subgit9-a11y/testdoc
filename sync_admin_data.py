
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

async def debug_schema_and_sync():
    db_url = os.getenv("DATABASE_URL")
    clean_url = db_url.replace("mysql+pymysql://", "")
    auth_part, rest = clean_url.split("@")
    user, password = auth_part.split(":")
    password = urllib.parse.unquote(password)
    host_port, dbname = rest.split("/")
    host = host_port.split(":")[0] if ":" in host_port else host_port
    port = int(host_port.split(":")[1]) if ":" in host_port else 3306
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    print("\n" + "="*60)
    print(f"ASTRA SCHEMA DISCOVERY & SYNC")
    print("="*60)
    
    try:
        mysql_conn = pymysql.connect(
            host=host, user=user, password=password, database=dbname, port=port,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=15
        )
        
        with mysql_conn.cursor() as cursor:
            # 1. Discover MySQL Columns
            print("\n🔍 Investigating Legacy MySQL Tables...")
            
            # Check 'users' columns
            cursor.execute("DESCRIBE users")
            user_cols = [row['Field'] for row in cursor.fetchall()]
            print(f"   [users] table columns: {user_cols}")
            
            # Check 'doctors' columns
            cursor.execute("DESCRIBE doctors")
            doc_cols = [row['Field'] for row in cursor.fetchall()]
            print(f"   [doctors] table columns: {doc_cols}")

            # 2. SYNC DOCTORS
            print("\n📦 Syncing Doctors...")
            try:
                # Map available columns
                sql = "SELECT * FROM doctors"
                cursor.execute(sql)
                legacy_docs = cursor.fetchall()
                for doc in legacy_docs:
                    # Map correctly
                    doc_data = {
                        "doctor_id": f"DOC-{doc.get('id')}",
                        "name": str(doc.get('name') or doc.get('full_name') or "Doctor"),
                        "specialization": str(doc.get('specialization') or doc.get('category') or 'General Physician'),
                        "consultation_fee": int(doc.get('consultation_fee') or 500),
                        "is_active": True
                    }
                    # Check if 'email' exists in legacy then add it to Sync payload IF 'doctors' in Supabase allows it
                    if 'email' in doc: doc_data['email'] = str(doc.get('email', ''))
                    
                    try:
                        supabase.table("doctors").upsert(doc_data).execute()
                        print(f"   ✅ Synced Doc: {doc_data['name']}")
                    except Exception as se:
                        print(f"   ❌ Supabase Error (Doc): {se}")
            except Exception as e:
                print(f"   ⚠️ Could not fetch from doctors table: {e}")

            # 3. SYNC PATIENTS
            print("\n📦 Syncing Patients...")
            try:
                # Find patient identifier
                where_clause = ""
                if 'role' in user_cols: where_clause = "WHERE role = 'patient'"
                elif 'user_type' in user_cols: where_clause = "WHERE user_type = 'patient'"
                
                sql = f"SELECT * FROM users {where_clause} LIMIT 50"
                cursor.execute(sql)
                legacy_pts = cursor.fetchall()
                
                for pt in legacy_pts:
                    pt_data = {
                        "patient_id": str(pt.get('id')),
                        "name": str(pt.get('name') or pt.get('first_name') or "Patient"),
                        "email": str(pt.get('email') or ""),
                        "phone": str(pt.get('phone_no') or pt.get('phone') or ""),
                        "is_active": True
                    }
                    try:
                        # Ensure we map to 'patient_profiles' correctly
                        supabase.table("patient_profiles").upsert(pt_data).execute()
                        print(f"   ✅ Synced Patient: {pt_data['name']}")
                    except Exception as pe:
                        print(f"   ❌ Supabase Error (Patient): {pe}")
            except Exception as e:
                print(f"   ⚠️ Could not sync patients: {e}")

        print("\n" + "="*60)
        print("SYNC COMPLETE!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\nConnection Error: {e}")
    finally:
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    asyncio.run(debug_schema_and_sync())
