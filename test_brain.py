import asyncio
import sys
import os
import json

# Add the app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from astra_brain_client import get_brain_client
    print("SUCCESS: Successfully imported AstraBrainClient")
except ImportError as e:
    print(f"ERROR: ImportError: {e}")
    sys.exit(1)

async def run_tests():
    client = get_brain_client()
    print("\nStarting Astra Brain Python Validation...")
    print("=" * 40)

    # Test 1: Health
    health = await client.check_health()
    h_res = "PASSED" if health.get('status') == 'online' else "FAILED"
    print(f"1. Health Check:      {h_res} ({health.get('status')})")

    # Test 2: Chat
    chat = await client.chat("Explain Guduchi")
    c_res = "PASSED" if chat.success else "FAILED"
    print(f"2. Chat/RAG:          {c_res}")
    if chat.success:
        print(f"   Response Preview:  {chat.answer[:50]}...")

    # Test 3: Safety
    safety = await client.analyze_safety("Is this safe?")
    s_res = "PASSED" if hasattr(safety, 'is_safe') else "FAILED"
    print(f"3. Safety Sentinel:   {s_res}")

    # Test 4: Emotion
    emotion = await client.detect_emotion("I feel great")
    e_res = "PASSED" if emotion.emotion else "FAILED"
    print(f"4. Emotion Detection: {e_res} (Detected: {emotion.emotion})")

    print("=" * 40)
    print("Validation Finished.")

if __name__ == "__main__":
    asyncio.run(run_tests())
