
import os
import pymysql
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def check_patient_profiles():
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
        print("\n--- COLUMNS IN [patient_profiles] ---")
        cursor.execute("DESCRIBE patient_profiles")
        for c in cursor.fetchall():
            print(f"- {c['Field']} ({c['Type']})")
        
        print("\nSample Data (first 5):")
        cursor.execute("SELECT * FROM patient_profiles LIMIT 5")
        for r in cursor.fetchall():
            print(r)

if __name__ == "__main__":
    check_patient_profiles()
