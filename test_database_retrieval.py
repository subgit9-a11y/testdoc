"""
Database Connection Test
Retrieves one doctor and one user from the MySQL database
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔍 DATABASE CONNECTION TEST")
print("=" * 70)

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL not found in environment variables")
    print("Please check your .env file")
    sys.exit(1)

print(f"\n📊 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")

try:
    # Create engine
    print("\n🔌 Connecting to database...")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True to see SQL queries
    )
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("✅ Database connection established!")
    
    # Test 1: Retrieve one doctor
    print("\n" + "=" * 70)
    print("👨‍⚕️  TEST 1: RETRIEVE DOCTOR DETAILS")
    print("=" * 70)
    
    try:
        # Check if doctors table exists
        result = db.execute(text("SHOW TABLES LIKE 'doctors'"))
        if result.fetchone():
            print("✅ 'doctors' table exists")
            
            # Get one doctor
            result = db.execute(text("""
                SELECT 
                    id, doctor_id, name, email, phone, 
                    specialization, experience_years, consultation_fee,
                    is_active, created_at
                FROM doctors 
                WHERE is_active = 1 
                LIMIT 1
            """))
            
            doctor = result.fetchone()
            
            if doctor:
                print("\n📋 Doctor Details:")
                print(f"   ID: {doctor[0]}")
                print(f"   Doctor ID: {doctor[1]}")
                print(f"   Name: {doctor[2]}")
                print(f"   Email: {doctor[3]}")
                print(f"   Phone: {doctor[4]}")
                print(f"   Specialization: {doctor[5]}")
                print(f"   Experience: {doctor[6]} years")
                print(f"   Consultation Fee: ₹{doctor[7]}")
                print(f"   Status: {'Active' if doctor[8] else 'Inactive'}")
                print(f"   Created: {doctor[9]}")
                print("\n✅ Successfully retrieved doctor details!")
            else:
                print("\n⚠️  No doctors found in database")
                print("💡 You may need to add doctors via Laravel admin panel")
        else:
            print("❌ 'doctors' table does not exist")
            print("💡 Please run database migrations")
    except Exception as e:
        print(f"❌ Error retrieving doctor: {e}")
    
    # Test 2: Retrieve one user
    print("\n" + "=" * 70)
    print("👤 TEST 2: RETRIEVE USER DETAILS")
    print("=" * 70)
    
    try:
        # Check if users table exists
        result = db.execute(text("SHOW TABLES LIKE 'users'"))
        if result.fetchone():
            print("✅ 'users' table exists")
            
            # Get one user
            result = db.execute(text("""
                SELECT 
                    id, email, name, picture, 
                    email_verified, created_at, updated_at
                FROM users 
                LIMIT 1
            """))
            
            user = result.fetchone()
            
            if user:
                print("\n📋 User Details:")
                print(f"   ID: {user[0]}")
                print(f"   Email: {user[1]}")
                print(f"   Name: {user[2]}")
                print(f"   Picture: {user[3][:50] if user[3] else 'None'}...")
                print(f"   Email Verified: {'Yes' if user[4] else 'No'}")
                print(f"   Created: {user[5]}")
                print(f"   Updated: {user[6]}")
                print("\n✅ Successfully retrieved user details!")
            else:
                print("\n⚠️  No users found in database")
                print("💡 Users will be created when they first authenticate via Firebase")
        else:
            print("❌ 'users' table does not exist")
            print("💡 Please run database migrations")
    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
    
    # Test 3: Check other important tables
    print("\n" + "=" * 70)
    print("📊 TEST 3: CHECK OTHER TABLES")
    print("=" * 70)
    
    important_tables = [
        'patient_profiles',
        'consultations',
        'prescription_records',
        'user_sessions'
    ]
    
    for table_name in important_tables:
        try:
            result = db.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
            if result.fetchone():
                # Count records
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = count_result.fetchone()[0]
                print(f"   ✅ {table_name}: {count} records")
            else:
                print(f"   ⚠️  {table_name}: Table not found")
        except Exception as e:
            print(f"   ❌ {table_name}: Error - {e}")
    
    # Test 4: Test patient data (if exists)
    print("\n" + "=" * 70)
    print("🏥 TEST 4: RETRIEVE PATIENT DETAILS")
    print("=" * 70)
    
    try:
        result = db.execute(text("SHOW TABLES LIKE 'patient_profiles'"))
        if result.fetchone():
            print("✅ 'patient_profiles' table exists")
            
            # Get one patient
            result = db.execute(text("""
                SELECT 
                    id, patient_id, patient_code, name, 
                    email, phone, age, gender, is_active
                FROM patient_profiles 
                WHERE is_active = 1 
                LIMIT 1
            """))
            
            patient = result.fetchone()
            
            if patient:
                print("\n📋 Patient Details:")
                print(f"   ID: {patient[0]}")
                print(f"   Patient ID: {patient[1]}")
                print(f"   Patient Code: {patient[2]}")
                print(f"   Name: {patient[3]}")
                print(f"   Email: {patient[4]}")
                print(f"   Phone: {patient[5]}")
                print(f"   Age: {patient[6]}")
                print(f"   Gender: {patient[7]}")
                print(f"   Status: {'Active' if patient[8] else 'Inactive'}")
                print("\n✅ Successfully retrieved patient details!")
            else:
                print("\n⚠️  No patients found in database")
        else:
            print("⚠️  'patient_profiles' table does not exist")
    except Exception as e:
        print(f"❌ Error retrieving patient: {e}")
    
    # Close connection
    db.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print("\n✅ Database connection: SUCCESS")
    print("✅ MySQL database is accessible")
    print("✅ Tables are queryable")
    print("\n💡 This database is shared with your Laravel admin panel")
    print("💡 Any data added in Laravel will appear here and vice versa")
    
    print("\n" + "=" * 70)
    print("🎉 DATABASE TEST COMPLETE!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ DATABASE CONNECTION FAILED!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check DATABASE_URL in .env file")
    print("2. Verify database credentials")
    print("3. Ensure database server is accessible")
    print("4. Check firewall settings")
    sys.exit(1)
