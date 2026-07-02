"""
Pre-Deployment Verification Script for Vultr
Run this on Vultr server before starting the app
"""
import sys
import os

def check_imports():
    """Check all critical imports"""
    errors = []
    
    print("Checking critical imports...")
    
    # Core modules
    try:
        from app.astra_brain_client import AstraBrainClient, get_brain_client
        print("  [OK] astra_brain_client")
    except Exception as e:
        errors.append(f"astra_brain_client: {e}")
        print(f"  [FAIL] astra_brain_client: {e}")
    
    try:
        from app.astra.pipeline import AstraPipeline
        print("  [OK] astra.pipeline")
    except Exception as e:
        errors.append(f"astra.pipeline: {e}")
        print(f"  [FAIL] astra.pipeline: {e}")
    
    try:
        from app.enhanced_inference import AstraModelInference
        print("  [OK] enhanced_inference")
    except Exception as e:
        errors.append(f"enhanced_inference: {e}")
        print(f"  [FAIL] enhanced_inference: {e}")
    
    try:
        from app.model_service import model_service
        print("  [OK] model_service")
    except Exception as e:
        errors.append(f"model_service: {e}")
        print(f"  [FAIL] model_service: {e}")
    
    try:
        from app.astra.brain_routes import router
        print("  [OK] brain_routes")
    except Exception as e:
        errors.append(f"brain_routes: {e}")
        print(f"  [FAIL] brain_routes: {e}")
    
    try:
        from app.ai_agent_api import router
        print("  [OK] ai_agent_api")
    except Exception as e:
        errors.append(f"ai_agent_api: {e}")
        print(f"  [FAIL] ai_agent_api: {e}")
    
    return errors

def check_env():
    """Check environment variables"""
    print("\nChecking environment...")
    
    required = ['SUPABASE_URL', 'SUPABASE_KEY']
    optional = ['SHOPIFY_STORE_URL', 'FIREBASE_CREDENTIALS']
    
    missing = []
    for var in required:
        if os.getenv(var):
            print(f"  [OK] {var}")
        else:
            print(f"  [WARN] {var} not set")
            missing.append(var)
    
    return missing

def check_dependencies():
    """Check Python dependencies"""
    print("\nChecking dependencies...")
    
    deps = ['fastapi', 'uvicorn', 'httpx', 'pydantic']
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"  [OK] {dep}")
        except ImportError:
            print(f"  [FAIL] {dep} not installed")
            missing.append(dep)
    
    return missing

def main():
    print("=" * 50)
    print("VULTR DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    import_errors = check_imports()
    env_issues = check_env()
    dep_issues = check_dependencies()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if not import_errors and not dep_issues:
        print("[SUCCESS] All checks passed!")
        print("\nTo start the server:")
        print("  uvicorn main:app --host 0.0.0.0 --port 5000")
        return 0
    else:
        print("[ISSUES FOUND]")
        if import_errors:
            print(f"  Import errors: {len(import_errors)}")
        if dep_issues:
            print(f"  Missing dependencies: {dep_issues}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
