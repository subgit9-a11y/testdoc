
import os
import pymysql
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def analyze_patients():
    db_url = os.getenv("DATABASE_URL")
    clean_url = db_url.replace("mysql+pymysql://", "")
    auth_part, rest = clean_url.split("@")
    user, password = auth_part.split(":")
    password = urllib.parse.unquote(password)
    host_port, dbname = rest.split("/")
    host = host_port.split(":")[0] if ":" in host_port else host_port
    
    conn = pymysql.connect(
        host=host, user=user, password=password, database=dbname,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        print("\n--- ANALYZING ALL POTENTIAL PATIENT DATA ---")
        
        # 1. Investigate [patients] table
        try:
            print("\nInvestigating [patients] table...")
            cursor.execute("SELECT * FROM patients LIMIT 10")
            patients_table_data = cursor.fetchall()
            if not patients_table_data:
                print("   [patients] table is EMPTY.")
            else:
                for p in patients_table_data:
                    print(f"   Patient ID: {p.get('id')} | Name: {p.get('name') or p.get('full_name')} | Age: {p.get('age')}")
        except Exception as e:
            print(f"   Could not query [patients] table: {e}")
            
        # 2. Investigate [users] table
        try:
            print("\nInvestigating [users] table for clinical patients...")
            # Usually patients have no doctor_id and role might be numeric
            cursor.execute("SELECT * FROM users WHERE name LIKE '%Subash%' OR email LIKE '%gmail.com%' LIMIT 10")
            user_data = cursor.fetchall()
            for u in user_data:
                print(f"   User ID: {u.get('id')} | Name: {u.get('name')} | Phone: {u.get('phone')}")
        except Exception as e:
            print(f"   Could not query [users] table: {e}")

        # 3. Check [appointments]
        try:
            print("\nChecking Appointments for patient cross-links...")
            cursor.execute("SELECT patient_id, COUNT(*) as count FROM appointments GROUP BY patient_id LIMIT 5")
            appt_data = cursor.fetchall()
            for a in appt_data:
                print(f"   Patient Link ID: {a['patient_id']} | Sessions: {a['count']}")
        except Exception as e:
            print(f"   Could not query [appointments] table: {e}")

if __name__ == "__main__":
    analyze_patients()
