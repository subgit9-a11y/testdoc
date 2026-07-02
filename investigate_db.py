
import os
import pymysql
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def investigate():
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
        print("\n--- TABLES AVAILABLE ---")
        cursor.execute("SHOW TABLES")
        tables = [list(r.values())[0] for r in cursor.fetchall()]
        print(tables)
        
        # Check patients specifically
        potential_pt_tables = [t for t in tables if 'patient' in t.lower()]
        print(f"\nPotential Patient Tables: {potential_pt_tables}")
        
        for table in tables:
            if table in ['users', 'patients', 'patient']:
                print(f"\n--- COLUMNS IN [{table}] ---")
                cursor.execute(f"DESCRIBE {table}")
                cols = cursor.fetchall()
                for c in cols:
                    print(f"- {c['Field']} ({c['Type']})")
                
                # Check for roles or specific groups
                print(f"\nSample data from [{table}] (first 5):")
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                data = cursor.fetchall()
                for d in data:
                    print(d)

if __name__ == "__main__":
    investigate()
