import pymysql

DB_CONFIG = {
    'host': '82.25.125.50',
    'user': 'u656934180_ayureze_admin',
    'password': 'nemke2-zokroj-Fibfez',
    'database': 'u656934180_ayureze',
    'port': 3306
}

def inspect_db():
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
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    inspect_db()
