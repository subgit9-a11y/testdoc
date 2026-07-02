"""
Quick Database Test - Retrieve Doctor and User
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DATABASE QUICK TEST")
print("=" * 60)

# Parse DATABASE_URL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found")
    exit(1)

# Extract connection details from URL
# Format: mysql+pymysql://user:pass@host:port/database
try:
    parts = db_url.replace("mysql+pymysql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1].replace("%2D", "-").replace("%2d", "-")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    database = host_db[1]
    
    print(f"\nConnecting to: {host}:{port}/{database}")
    
    # Connect
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=10
    )
    
    print("✅ Connected!")
    
    cursor = conn.cursor()
    
    # Test 1: Get one doctor
    print("\n" + "-" * 60)
    print("DOCTOR DETAILS:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT name, email, specialization, experience_years, consultation_fee
        FROM doctors 
        WHERE is_active = 1 
        LIMIT 1
    """)
    
    doctor = cursor.fetchone()
    if doctor:
        print(f"Name: {doctor[0]}")
        print(f"Email: {doctor[1]}")
        print(f"Specialization: {doctor[2]}")
        print(f"Experience: {doctor[3]} years")
        print(f"Fee: ₹{doctor[4]}")
        print("✅ Doctor retrieved successfully!")
    else:
        print("⚠️  No doctors found")
    
    # Test 2: Get one user
    print("\n" + "-" * 60)
    print("USER DETAILS:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT id, email, name, email_verified
        FROM users 
        LIMIT 1
    """)
    
    user_data = cursor.fetchone()
    if user_data:
        print(f"ID: {user_data[0]}")
        print(f"Email: {user_data[1]}")
        print(f"Name: {user_data[2]}")
        print(f"Verified: {'Yes' if user_data[3] else 'No'}")
        print("✅ User retrieved successfully!")
    else:
        print("⚠️  No users found")
    
    # Count tables
    print("\n" + "-" * 60)
    print("TABLE COUNTS:")
    print("-" * 60)
    
    tables = ['doctors', 'users', 'patient_profiles', 'consultations']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        except:
            print(f"{table}: Not found")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE TEST COMPLETE!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nCheck your DATABASE_URL in .env file")
