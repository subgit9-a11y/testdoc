import asyncio
import sys
import os
import json

# Add the app directory to sys.path so we can import the client
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from astra_brain_client import get_brain_client, Intent
    print("SUCCESS: System: Successfully linked to AstraBrainClient.")
except ImportError as e:
    print(f"ERROR: System Error: Cannot find astra_brain_client.py. {e}")
    sys.exit(1)

async def run_comprehensive_test():
    client = get_brain_client()
    
    print("\n" + "="*50)
    print("ASTRA AI BRAIN - FULL ENDPOINT VALIDATION")
    print("="*50)

    # 1. Health Check
    health = await client.check_health()
    h_msg = "PASSED" if health.get("status") == "online" else "FAILED"
    print(f"[1] Health Status:    {health.get('status').upper()} ({h_msg})")

    # 2. Core Chat / RAG
    print(f"RUNNING: [2] Chat / RAG:        Testing prefix stripping...", flush=True)
    chat = await client.chat("Explain the benefits of Ashwagandha")
    if chat.success:
        print(f"PASSED: [2] Chat / RAG:        Clean Response")
        print(f"   [Preview]: {chat.answer[:85]}...")
    else:
        print(f"FAILED: [2] Chat / RAG:        Error returned")

    # 3. Autopilot (Intent Routing)
    print(f"RUNNING: [3] Autopilot:         Routing query...", flush=True)
    auto = await client.autopilot("I want to book an appointment with a doctor")
    if auto.status == "success":
        print(f"PASSED: [3] Autopilot:         Intent: {auto.intent}")
    else:
        print(f"FAILED: [3] Autopilot:         Error returned")

    # 4. Safety Sentinel
    print(f"RUNNING: [4] Safety Sentinel:   Analyzing risk...", flush=True)
    safety = await client.analyze_safety("I need medical advice for a fever.")
    if safety.is_safe:
        print(f"PASSED: [4] Safety Sentinel:   Content is Safe")
    else:
        print(f"WARNING: [4] Safety Sentinel:   Flagged (Check Logic)")

    # 5. Emotion Analysis
    print(f"RUNNING: [5] Emotion Detection: Detecting sentiment...", flush=True)
    emotion = await client.detect_emotion("I am feeling much better now, thank you!")
    if emotion.emotion:
        print(f"PASSED: [5] Emotion Detection: Mood: {emotion.emotion}")
    else:
        print(f"FAILED: [5] Emotion Detection: Error returned")

    print("="*50)
    print("VALIDATION COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
