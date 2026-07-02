
import os
import pymysql
import asyncio
import urllib.parse
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Any, Optional
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

class AstraSynergyPipeline:
    def __init__(self):
        # Database Connections
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        db_url = os.getenv("DATABASE_URL")
        clean_url = db_url.replace("mysql+pymysql://", "")
        auth_part, rest = clean_url.split("@")
        user, password = auth_part.split(":")
        password = urllib.parse.unquote(password)
        host_port, dbname = rest.split("/")
        host = host_port.split(":")[0] if ":" in host_port else host_port
        port = int(host_port.split(":")[1]) if ":" in host_port else 3306
        
        self._mysql_config = {
            "host": host, "user": user, "password": password,
            "database": dbname, "port": port, "connect_timeout": 15
        }

    async def sync_data_synergy(self, limit: int = 50):
        """Perform a clean sync without unique constraint violations."""
        print("\n" + "="*80)
        print("ASTRA SYNERGY PIPELINE: CLEAN SYNCHRONIZATION RUN")
        print("="*80)
        
        try:
            # 1. Fetch existing doctor IDs from Supabase to avoid duplicates
            print("\n🔍 Checking existing Astra Registry...")
            res_d = self.supabase.table("doctors").select("doctor_id").execute()
            existing_doc_ids = {d['doctor_id'] for d in res_d.data}
            
            res_p = self.supabase.table("patient_profiles").select("patient_code").execute()
            existing_pat_codes = {p['patient_code'] for p in res_p.data}
            print(f"   Found {len(existing_doc_ids)} existing doctors and {len(existing_pat_codes)} existing patients.")

            # 2. Connect to MySQL
            conn = pymysql.connect(**self._mysql_config, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cursor:
                
                # --- SYNC DOCTORS ---
                print("\n👨‍⚕️ Mirroring Licensed Doctors from MySQL...")
                cursor.execute("SELECT * FROM doctors")
                doctors = cursor.fetchall()
                for doc in doctors:
                    did = f"DOC-{doc['id']}"
                    if did in existing_doc_ids:
                        continue # Already synced

                    doc_data = {
                        "doctor_id": did,
                        "name": str(doc.get('name') or "Doctor"),
                        "specialization": str(doc.get('specialization') or 'GP'),
                        "consultation_fee": int(doc.get('consultation_fee') or 500),
                        "is_active": True
                    }
                    try:
                        self.supabase.table("doctors").insert(doc_data).execute()
                        print(f"   ✅ New Doctor: {doc_data['name']}")
                    except Exception as e:
                        print(f"   ❌ Skip {did}: {e}")

                # --- SYNC PATIENTS ---
                print("\n👤 Mirroring Real Patients from MySQL [patient_profiles]...")
                try:
                    cursor.execute("SELECT * FROM patient_profiles")
                    patients = cursor.fetchall()
                    for pt in patients:
                        pcode = str(pt.get('patient_code'))
                        if pcode in existing_pat_codes:
                            continue # Already exists

                        pt_data = {
                            "id": str(pt.get('id')), 
                            "patient_id": str(pt.get('patient_id') or pt.get('id')),
                            "patient_code": pcode,
                            "name": str(pt.get('name')),
                            "phone": str(pt.get('phone') or ""),
                            "email": str(pt.get('email') or ""),
                            "is_active": True
                        }
                        try:
                            self.supabase.table("patient_profiles").insert(pt_data).execute()
                            print(f"   ✅ New Patient: {pt_data['name']}")
                        except Exception as e:
                            print(f"   ❌ Skip {pcode}: {e}")
                except Exception as e:
                    print(f"   ⚠️ Patient Sync issue: {e}")

            print("\n" + "="*80)
            print("PIPELINE SYNC SUCCESSFUL!")
            print("="*80)

        except Exception as e:
            print(f"❌ Connection Error: {e}")
        finally:
            if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    p = AstraSynergyPipeline()
    asyncio.run(p.sync_data_synergy())
