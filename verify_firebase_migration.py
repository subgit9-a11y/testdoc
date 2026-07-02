"""
Quick Firebase Migration Verification
Checks if the migration was successful without heavy imports
"""

import os
import re

print("=" * 60)
print("🔥 FIREBASE MIGRATION VERIFICATION")
print("=" * 60)

# Check .env file
print("\n1. Checking .env file...")
try:
    with open('.env', 'r') as f:
        env_content = f.read()
        
    if 'AUTH0_DOMAIN' in env_content or 'AUTH0_CLIENT_ID' in env_content:
        print("   ❌ Auth0 variables still present in .env")
    else:
        print("   ✅ No Auth0 variables in .env")
    
    if 'FIREBASE_CREDENTIAL_PATH' in env_content:
        print("   ✅ Firebase credential path configured")
    else:
        print("   ⚠️  Firebase credential path not found")
except Exception as e:
    print(f"   ❌ Error reading .env: {e}")

# Check auth.py
print("\n2. Checking app/auth.py...")
try:
    with open('app/auth.py', 'r') as f:
        auth_content = f.read()
    
    if 'firebase_admin' in auth_content and 'from firebase_admin import' in auth_content:
        print("   ✅ Firebase Admin SDK imported")
    else:
        print("   ❌ Firebase Admin SDK not found")
    
    if 'verify_id_token' in auth_content:
        print("   ✅ Firebase token verification implemented")
    else:
        print("   ❌ Firebase token verification not found")
except Exception as e:
    print(f"   ❌ Error reading auth.py: {e}")

# Check database_models.py
print("\n3. Checking app/database_models.py...")
try:
    with open('app/database_models.py', 'r') as f:
        db_content = f.read()
    
    if 'Firebase user information' in db_content:
        print("   ✅ User model updated for Firebase")
    else:
        print("   ⚠️  User model may still reference Auth0")
    
    if 'firebase_login' in db_content:
        print("   ✅ Session metadata updated for Firebase")
    else:
        print("   ⚠️  Session metadata may still reference Auth0")
except Exception as e:
    print(f"   ❌ Error reading database_models.py: {e}")

# Check env_validator.py
print("\n4. Checking app/env_validator.py...")
try:
    with open('app/env_validator.py', 'r') as f:
        validator_content = f.read()
    
    if 'FIREBASE_CREDENTIAL_PATH' in validator_content:
        print("   ✅ Firebase credential path in validator")
    else:
        print("   ⚠️  Firebase credential path not in validator")
    
    if 'AUTH0_DOMAIN' in validator_content or 'AUTH0_CLIENT_ID' in validator_content:
        print("   ⚠️  Auth0 variables still in validator")
    else:
        print("   ✅ No Auth0 variables in validator")
except Exception as e:
    print(f"   ❌ Error reading env_validator.py: {e}")

# Check for Firebase credential file
print("\n5. Checking Firebase credential file...")
firebase_path = os.getenv('FIREBASE_CREDENTIAL_PATH', 'firebase-service-account.json')
if os.path.exists(firebase_path):
    print(f"   ✅ Firebase credential file found at: {firebase_path}")
elif os.path.exists('aiastra/firebase-service-account.json'):
    print(f"   ⚠️  Firebase credential file found at: aiastra/firebase-service-account.json")
    print(f"   💡 Consider updating FIREBASE_CREDENTIAL_PATH to: aiastra/firebase-service-account.json")
else:
    print(f"   ❌ Firebase credential file not found")

print("\n" + "=" * 60)
print("✅ MIGRATION VERIFICATION COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Ensure firebase-service-account.json is in the correct location")
print("2. Run: python main.py")
print("3. Test authentication with Firebase ID tokens")
print("=" * 60)
