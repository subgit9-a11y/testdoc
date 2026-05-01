import os
import pymysql

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '82.25.125.50'),
    'user': os.environ.get('DB_USER', 'u656934180_ayureze_admin'),
    'password': os.environ.get('DB_PASSWORD', 'nemke2-zokroj-Fibfez'), # IMPORTANT: It is strongly recommended to remove the fallback password and set it strictly via environment variables.
    'database': os.environ.get('DB_NAME', 'u656934180_ayureze'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def inspect_db():
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # 1. List all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in u656934180_ayureze:")
            for (table,) in tables:
                print(f"- {table}")
            
            # 2. Find doctor related tables
            doctor_tables = [t[0] for t in tables if 'doctor' in t[0].lower()]
            print(f"\nPotential Doctor Tables: {doctor_tables}")
            
            for table in doctor_tables:
                print(f"\n--- Structure of '{table}' ---")
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                for col in columns:
                    print(col)
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    inspect_db()
