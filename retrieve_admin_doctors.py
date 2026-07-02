
import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_real_admin_doctors():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    # Parse mysql+pymysql://user:pass@host:port/dbname
    # We strip the prefix for pymysql.connect
    clean_url = db_url.replace("mysql+pymysql://", "")
    auth_part, rest = clean_url.split("@")
    user, password = auth_part.split(":")
    # Replace URL-encoded characters in password if any (e.g. %2D)
    import urllib.parse
    password = urllib.parse.unquote(password)
    
    host_port, dbname = rest.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 3306

    print(f"Connecting to Admin DB: {host} / {dbname}...")
    
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=dbname,
            port=port,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        
        with connection.cursor() as cursor:
            # Try common table names for doctors in legacy systems
            tables = ["doctors", "doctor"]
            success = False
            for table in tables:
                try:
                    sql = f"SELECT * FROM {table} LIMIT 5"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if result:
                        print(f"\n--- REAL DOCTORS FROM {table.upper()} TABLE ---")
                        for d in result:
                            # Print common columns
                            print(f"ID: {d.get('id')}")
                            print(f"Name: {d.get('name') or d.get('full_name')}")
                            print(f"Email: {d.get('email')}")
                            print(f"Specialty: {d.get('specialty') or d.get('category')}")
                            print("-" * 30)
                        success = True
                except:
                    continue
            
            if not success:
                print("Could not find data in standard doctor tables.")
                # List tables to see what's there
                cursor.execute("SHOW TABLES")
                print("\nAvailable Tables:")
                for row in cursor.fetchall():
                    print(f"- {list(row.values())[0]}")

    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    get_real_admin_doctors()
