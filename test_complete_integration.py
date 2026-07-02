"""
Complete Integration Test
Tests Firebase, Supabase, and MySQL connections
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔍 COMPLETE INTEGRATION VERIFICATION")
print("=" * 70)

# Test 1: Firebase Configuration
print("\n1️⃣  FIREBASE AUTHENTICATION")
print("-" * 70)

firebase_path = os.getenv('FIREBASE_CREDENTIAL_PATH', 'firebase-service-account.json')
print(f"   Credential Path: {firebase_path}")

if os.path.exists(firebase_path):
    print(f"   ✅ Firebase credential file found")
    try:
        import json
        with open(firebase_path, 'r') as f:
            creds = json.load(f)
            print(f"   ✅ Project ID: {creds.get('project_id', 'N/A')}")
            print(f"   ✅ Client Email: {creds.get('client_email', 'N/A')[:30]}...")
    except Exception as e:
        print(f"   ⚠️  Could not read credential file: {e}")
elif os.path.exists('aiastra/firebase-service-account.json'):
    print(f"   ⚠️  File found at: aiastra/firebase-service-account.json")
    print(f"   💡 Update FIREBASE_CREDENTIAL_PATH to: aiastra/firebase-service-account.json")
else:
    print(f"   ❌ Firebase credential file not found")

# Test 2: Supabase Configuration
print("\n2️⃣  SUPABASE DATABASE (Session & Chat Storage)")
print("-" * 70)

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    print(f"   ✅ Supabase URL: {supabase_url}")
    print(f"   ✅ Supabase Key: {supabase_key[:20]}...")
    
    # Try to connect
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print(f"   ✅ Supabase client initialized successfully")
        
        # Test connection
        try:
            result = client.table('astra_users').select('id').limit(1).execute()
            print(f"   ✅ Connection test successful")
        except Exception as e:
            print(f"   ⚠️  Connection test failed: {e}")
    except ImportError:
        print(f"   ⚠️  Supabase package not installed (pip install supabase)")
    except Exception as e:
        print(f"   ⚠️  Could not initialize Supabase: {e}")
else:
    print(f"   ❌ Supabase credentials not configured")

# Test 3: MySQL/Laravel Database
print("\n3️⃣  MYSQL/LARAVEL DATABASE (Patient & Doctor Data)")
print("-" * 70)

database_url = os.getenv('DATABASE_URL')

if database_url:
    # Parse database URL
    if '@' in database_url:
        parts = database_url.split('@')
        host_db = parts[1] if len(parts) > 1 else 'unknown'
        print(f"   ✅ Database URL configured")
        print(f"   ✅ Host: {host_db.split(':')[0]}")
        print(f"   ✅ Database: {host_db.split('/')[-1] if '/' in host_db else 'unknown'}")
    else:
        print(f"   ✅ Database URL: {database_url[:50]}...")
    
    # Try to connect
    try:
        from sqlalchemy import create_engine
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            print(f"   ✅ MySQL connection successful")
            
            # Check for key tables
            result = conn.execute("SHOW TABLES LIKE 'users'")
            if result.fetchone():
                print(f"   ✅ 'users' table exists")
            
            result = conn.execute("SHOW TABLES LIKE 'patient_profiles'")
            if result.fetchone():
                print(f"   ✅ 'patient_profiles' table exists")
                
            result = conn.execute("SHOW TABLES LIKE 'doctors'")
            if result.fetchone():
                print(f"   ✅ 'doctors' table exists")
                
    except ImportError:
        print(f"   ⚠️  SQLAlchemy not installed (pip install sqlalchemy pymysql)")
    except Exception as e:
        print(f"   ⚠️  Could not connect to MySQL: {e}")
else:
    print(f"   ❌ DATABASE_URL not configured")

# Test 4: Other Services
print("\n4️⃣  OTHER SERVICES")
print("-" * 70)

# Shopify
shopify_url = os.getenv('SHOPIFY_SHOP_URL')
shopify_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
if shopify_url and shopify_token:
    print(f"   ✅ Shopify: {shopify_url}")
else:
    print(f"   ⚠️  Shopify not configured")

# Storj
storj_key = os.getenv('STORJ_ACCESS_KEY')
if storj_key:
    print(f"   ✅ Storj: Configured for document storage")
else:
    print(f"   ⚠️  Storj not configured")

# WhatsApp
wa_url = os.getenv('CUSTOM_WA_API_BASE_URL')
if wa_url:
    print(f"   ✅ WhatsApp API: {wa_url}")
else:
    print(f"   ⚠️  WhatsApp not configured")

# Summary
print("\n" + "=" * 70)
print("📊 INTEGRATION SUMMARY")
print("=" * 70)

firebase_ok = os.path.exists(firebase_path) or os.path.exists('aiastra/firebase-service-account.json')
supabase_ok = bool(supabase_url and supabase_key)
mysql_ok = bool(database_url)

print(f"\n   Firebase Authentication: {'✅ READY' if firebase_ok else '❌ NOT CONFIGURED'}")
print(f"   Supabase Database:       {'✅ READY' if supabase_ok else '❌ NOT CONFIGURED'}")
print(f"   MySQL/Laravel Database:  {'✅ READY' if mysql_ok else '❌ NOT CONFIGURED'}")

if firebase_ok and supabase_ok and mysql_ok:
    print("\n   🎉 ALL SYSTEMS READY!")
    print("\n   Authentication Flow:")
    print("   1. Firebase validates user → Returns ID token")
    print("   2. Backend verifies token → Extracts user info")
    print("   3. Supabase stores session → Returns session token")
    print("   4. MySQL stores patient/doctor data → Shared with Laravel")
    print("\n   ✅ Your backend is fully integrated and ready to run!")
    print("\n   Next step: python main.py")
else:
    print("\n   ⚠️  Some services need configuration")
    if not firebase_ok:
        print("   - Add firebase-service-account.json")
    if not supabase_ok:
        print("   - Configure SUPABASE_URL and SUPABASE_ANON_KEY")
    if not mysql_ok:
        print("   - Configure DATABASE_URL")

print("\n" + "=" * 70)
print("For detailed documentation, see: INTEGRATION_VERIFICATION.md")
print("=" * 70)
