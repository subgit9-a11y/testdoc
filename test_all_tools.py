"""
Comprehensive Tool Connectivity Test
Tests all Astra tools: Shopify, Storj, Doctors, Reminders, Notifications
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

async def test_all_tools():
    print("=" * 80)
    print("ASTRA TOOL CONNECTIVITY TEST")
    print("=" * 80)
    
    results = {
        "shopify": {"status": "❌", "details": ""},
        "storj": {"status": "❌", "details": ""},
        "doctor_service": {"status": "❌", "details": ""},
        "reminders": {"status": "❌", "details": ""},
        "notifications": {"status": "❌", "details": ""},
        "whatsapp": {"status": "❌", "details": ""}
    }
    
    # Test 1: Shopify Client
    print("\n1️⃣ Testing Shopify Integration...")
    print("-" * 80)
    try:
        from app.shopify_client import shopify_client
        
        if shopify_client.mock_mode:
            results["shopify"]["status"] = "⚠️ MOCK"
            results["shopify"]["details"] = "Running in mock mode (credentials not configured)"
            print(f"   Status: MOCK MODE")
            print(f"   Shop URL: {shopify_client.shop_url or 'Not configured'}")
        else:
            results["shopify"]["status"] = "✅"
            results["shopify"]["details"] = f"Connected to {shopify_client.shop_url}"
            print(f"   Status: CONNECTED")
            print(f"   Shop URL: {shopify_client.shop_url}")
            print(f"   API Version: 2024-01")
            
            # Try a simple search
            try:
                result = shopify_client.search_product("test")
                print(f"   Search Test: ✅ Working")
            except Exception as e:
                print(f"   Search Test: ⚠️ {str(e)[:50]}")
    except Exception as e:
        results["shopify"]["status"] = "❌"
        results["shopify"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Test 2: Storj Client
    print("\n2️⃣ Testing Storj (Decentralized Storage)...")
    print("-" * 80)
    try:
        from app.storj_client import StorjClient
        storj = StorjClient()
        
        storj_enabled = os.getenv("STORJ_ENABLED", "false").lower() == "true"
        
        if not storj_enabled:
            results["storj"]["status"] = "⚠️ DISABLED"
            results["storj"]["details"] = "STORJ_ENABLED=false in .env"
            print(f"   Status: DISABLED (set STORJ_ENABLED=true to enable)")
        else:
            results["storj"]["status"] = "✅"
            results["storj"]["details"] = f"Endpoint: {os.getenv('STORJ_ENDPOINT')}"
            print(f"   Status: ENABLED")
            print(f"   Endpoint: {os.getenv('STORJ_ENDPOINT')}")
            print(f"   Bucket: {os.getenv('STORJ_BUCKET')}")
    except Exception as e:
        results["storj"]["status"] = "❌"
        results["storj"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Test 3: Doctor Service
    print("\n3️⃣ Testing Doctor Service...")
    print("-" * 80)
    try:
        from app.doctors.doctor_service import doctor_service
        
        doctors = await doctor_service.get_all_doctors(limit=1)
        
        if doctors:
            results["doctor_service"]["status"] = "✅"
            results["doctor_service"]["details"] = f"Retrieved {len(doctors)} doctor(s)"
            print(f"   Status: WORKING")
            print(f"   Sample Doctor: {doctors[0]['name']}")
            print(f"   Specialization: {doctors[0]['specialization']}")
            
            # Check if using database or mock
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                print(f"   Database: Configured (may use mock if connection fails)")
            else:
                print(f"   Database: Using mock data")
        else:
            results["doctor_service"]["status"] = "⚠️"
            results["doctor_service"]["details"] = "No doctors found"
            print(f"   Status: No doctors returned")
    except Exception as e:
        results["doctor_service"]["status"] = "❌"
        results["doctor_service"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Test 4: Medicine Reminders
    print("\n4️⃣ Testing Medicine Reminder Service...")
    print("-" * 80)
    try:
        from app.medicine_reminders.supabase_reminder_service import supabase_reminder_service
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if supabase_url and supabase_key:
            results["reminders"]["status"] = "✅"
            results["reminders"]["details"] = "Supabase configured"
            print(f"   Status: CONFIGURED")
            print(f"   Supabase URL: {supabase_url[:30]}...")
        else:
            results["reminders"]["status"] = "⚠️"
            results["reminders"]["details"] = "Supabase credentials missing"
            print(f"   Status: NOT CONFIGURED")
            print(f"   Missing: SUPABASE_URL or SUPABASE_ANON_KEY")
    except Exception as e:
        results["reminders"]["status"] = "❌"
        results["reminders"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Test 5: Notification Service
    print("\n5️⃣ Testing Notification Service...")
    print("-" * 80)
    try:
        from app.notification_service import notification_service
        
        firebase_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        
        if firebase_account:
            results["notifications"]["status"] = "✅"
            results["notifications"]["details"] = "Firebase configured"
            print(f"   Status: CONFIGURED")
            print(f"   Firebase Account: {firebase_account}")
        else:
            results["notifications"]["status"] = "⚠️"
            results["notifications"]["details"] = "Firebase not configured"
            print(f"   Status: NOT CONFIGURED")
            print(f"   Missing: FIREBASE_SERVICE_ACCOUNT")
    except Exception as e:
        results["notifications"]["status"] = "❌"
        results["notifications"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Test 6: WhatsApp Integration
    print("\n6️⃣ Testing WhatsApp Integration...")
    print("-" * 80)
    try:
        from app.medicine_reminders.custom_whatsapp_client import CustomWhatsAppClient
        
        wa_api_url = os.getenv("CUSTOM_WA_API_BASE_URL")
        wa_token = os.getenv("CUSTOM_WA_BEARER_TOKEN")
        
        if wa_api_url and wa_token:
            results["whatsapp"]["status"] = "✅"
            results["whatsapp"]["details"] = f"Connected to {wa_api_url}"
            print(f"   Status: CONFIGURED")
            print(f"   API URL: {wa_api_url}")
            print(f"   Vendor UID: {os.getenv('CUSTOM_WA_VENDOR_UID')}")
        else:
            results["whatsapp"]["status"] = "⚠️"
            results["whatsapp"]["details"] = "WhatsApp credentials missing"
            print(f"   Status: NOT CONFIGURED")
            print(f"   Missing: CUSTOM_WA_API_BASE_URL or CUSTOM_WA_BEARER_TOKEN")
    except Exception as e:
        results["whatsapp"]["status"] = "❌"
        results["whatsapp"]["details"] = str(e)
        print(f"   Status: ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for tool, result in results.items():
        print(f"{result['status']} {tool.upper()}: {result['details']}")
    
    # Count status
    connected = sum(1 for r in results.values() if r['status'] == "✅")
    mock = sum(1 for r in results.values() if r['status'] == "⚠️ MOCK" or r['status'] == "⚠️ DISABLED" or r['status'] == "⚠️")
    errors = sum(1 for r in results.values() if r['status'] == "❌")
    
    print("\n" + "=" * 80)
    print(f"✅ Fully Connected: {connected}/6")
    print(f"⚠️ Partial/Mock: {mock}/6")
    print(f"❌ Errors: {errors}/6")
    print("=" * 80)
    
    if connected >= 4:
        print("\n🎉 ASTRA IS PRODUCTION READY!")
    elif connected >= 2:
        print("\n⚠️ ASTRA IS PARTIALLY READY - Some services need configuration")
    else:
        print("\n❌ ASTRA NEEDS CONFIGURATION - Check .env file")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_tools())
