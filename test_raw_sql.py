import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_raw_sql():
    if not DATABASE_URL:
        print("DATABASE_URL not found")
        return

    # DATABASE_URL=mysql+pymysql://u656934180_ayureze_admin:password@82.25.125.50:3306/u656934180_ayureze
    # Parse the URL manually for pymysql
    try:
        url = DATABASE_URL.replace("mysql+pymysql://", "")
        auth, rest = url.split("@")
        user, password = auth.split(":")
        host_port, db_name = rest.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
            
        print(f"Connecting to {host}:{port}/{db_name} as {user}...")
        
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=port,
            connect_timeout=10
        )
        
        with conn.cursor() as cursor:
            # Check for tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tables: {tables}")
            
            # Check for generic doctors table
            cursor.execute("SELECT COUNT(*) FROM doctors")
            count = cursor.fetchone()
            print(f"Doctor count: {count[0]}")
            
            # Get 5 doctors
            cursor.execute("SELECT * FROM doctors LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_sql()
