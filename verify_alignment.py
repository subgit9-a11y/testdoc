import asyncio
import json
import os
import sys

# Ensure our app is in path
sys.path.append(os.getcwd())

async def verify_braiin_integration():
    from app.astra_brain_client import AstraBrainClient
    client = AstraBrainClient()
    
    print("Starting Astra Brain Integration Test...")
    print("------------------------------------------")
    
    # 1. Health
    print("1. Checking Health...", end=" ", flush=True)
    health = await client.check_health()
    print(f"PASSED {health}" if health.get("status") == "online" else f"FAILED {health}")
    
    # 2. Chat
    print("2. Testing Chat...", end=" ", flush=True)
    chat = await client.chat("What is the best herb for immunity during winter?")
    if chat.success and chat.answer:
        print(f"PASSED Received response ({len(chat.answer)} chars)")
    else:
        print(f"FAILED: {chat}")
        
    # 3. Safety Analysis
    print("3. Testing Safety...", end=" ", flush=True)
    safety = await client.analyze_safety("I have high fever and chest pains.")
    if safety.is_safe is not None:
        print(f"PASSED Result: Safe={safety.is_safe}, Flags={safety.flags}")
    else:
        print("FAILED safety check")
        
    # 4. Emotion Detection
    print("4. Testing Emotion...", end=" ", flush=True)
    emotion = await client.detect_emotion("I am really frustrated with my backache.")
    if emotion.emotion:
        print(f"PASSED Detected: {emotion.emotion} ({emotion.intensity})")
    else:
        print("FAILED emotion detection")
        
    # 5. Wellness Generation
    print("5. Testing Wellness...", end=" ", flush=True)
    wellness = await client.generate_wellness("Winter Immunity Plan", "5 mins")
    if wellness.get("success"):
        print(f"PASSED Content: {len(wellness.get('content', ''))} chars")
    else:
        print("FAILED wellness generation")

    # 6. Fill (Extraction)
    print("6. Testing Fill...", end=" ", flush=True)
    extracted = await client.fill("Patient has cough since 4 days.", "{'duration': 'string'}")
    if extracted.get("success"):
        print(f"PASSED Extracted: {extracted.get('extracted_data')}")
    else:
        print("FAILED extraction")


    print("------------------------------------------")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(verify_braiin_integration())
