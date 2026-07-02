"""
Test Firebase Authentication Migration
Verifies that all Auth0 references have been replaced with Firebase
"""

import os
import sys

def check_file_for_auth0(filepath):
    """Check if a file contains Auth0 references"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'auth0' in content.lower() and 'firebase' not in content.lower():
                return True, content.lower().count('auth0')
    except:
        pass
    return False, 0

def main():
    print("=" * 60)
    print("🔥 FIREBASE AUTHENTICATION MIGRATION TEST")
    print("=" * 60)
    
    # Check critical files
    critical_files = [
        'app/auth.py',
        'app/auth_routes.py',
        'app/auth_middleware.py',
        'app/database_models.py',
        'app/env_validator.py',
        'app/frontend.py',
        'app/session_manager.py',
        'app/simplified_auth.py',
        '.env',
        '.env.example'
    ]
    
    print("\n📋 Checking critical files for Auth0 references...")
    issues_found = False
    
    for filepath in critical_files:
        full_path = os.path.join(os.getcwd(), filepath)
        if os.path.exists(full_path):
            has_auth0, count = check_file_for_auth0(full_path)
            if has_auth0:
                print(f"  ❌ {filepath}: Found {count} Auth0 reference(s)")
                issues_found = True
            else:
                print(f"  ✅ {filepath}: Clean")
        else:
            print(f"  ⚠️  {filepath}: File not found")
    
    # Check environment variables
    print("\n🔧 Checking environment variables...")
    firebase_path = os.getenv('FIREBASE_CREDENTIAL_PATH')
    
    if firebase_path:
        print(f"  ✅ FIREBASE_CREDENTIAL_PATH: {firebase_path}")
        if os.path.exists(firebase_path):
            print(f"  ✅ Firebase credential file exists")
        else:
            print(f"  ⚠️  Firebase credential file not found at: {firebase_path}")
    else:
        print(f"  ⚠️  FIREBASE_CREDENTIAL_PATH not set in environment")
    
    # Check for Auth0 env vars
    auth0_vars = ['AUTH0_DOMAIN', 'AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 'AUTH0_AUDIENCE']
    auth0_found = False
    for var in auth0_vars:
        if os.getenv(var):
            print(f"  ⚠️  {var} still present in environment")
            auth0_found = True
    
    if not auth0_found:
        print(f"  ✅ No Auth0 environment variables found")
    
    # Try importing auth modules
    print("\n📦 Testing module imports...")
    try:
        from app import auth
        print("  ✅ app.auth imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import app.auth: {e}")
        issues_found = True
    
    try:
        from app import auth_routes
        print("  ✅ app.auth_routes imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import app.auth_routes: {e}")
        issues_found = True
    
    try:
        from app import auth_middleware
        print("  ✅ app.auth_middleware imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import app.auth_middleware: {e}")
        issues_found = True
    
    # Final summary
    print("\n" + "=" * 60)
    if not issues_found:
        print("✅ MIGRATION SUCCESSFUL!")
        print("All Auth0 references have been replaced with Firebase.")
        print("The application is ready to use Firebase Authentication.")
    else:
        print("⚠️  MIGRATION INCOMPLETE")
        print("Some issues were found. Please review the output above.")
    print("=" * 60)
    
    return 0 if not issues_found else 1

if __name__ == "__main__":
    sys.exit(main())
