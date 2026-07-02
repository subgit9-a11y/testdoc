import asyncio
import os
import json
import httpx
from typing import List

# Load environment variables from .env.txt if present
if os.path.exists('.env.txt'):
    with open('.env.txt', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

# Import the AstraBrainClient used throughout the project
try:
    from app.astra_brain_client import AstraBrainClient
except ImportError:
    print('Error: Could not import AstraBrainClient. Ensure you run from project root.')
    exit(1)

async def mock_patient_flow():
    client = AstraBrainClient()
    # Extend timeout for deep responses
    client.client.timeout = httpx.Timeout(300.0, read=300.0, connect=10.0)

    print('\n=== Mock Real-Patient Journey ===\n')

    # 1️⃣ Health intake (AstraFill) – sample text
    fill_text = "Patient Maya, age 34, complains of intermittent lower back pain, occasional numbness in the right leg, and difficulty sleeping. She follows a vegetarian diet and reports high stress at work."
    fill_schema = '{"patient_name": "string", "age": "number", "symptoms": "list", "duration": "string"}'
    print('Step 1: AstraFill – Entity Extraction')
    fill_res = await client.fill(fill_text, fill_schema)
    print('Result:', json.dumps(fill_res, indent=2) if isinstance(fill_res, dict) else fill_res)
    print('-' * 60)

    # 2️⃣ Basic chat
    print('Step 2: Brain Chat – Basic Greeting')
    chat_res = await client.chat('Hello, I would like a quick health tip for better sleep.')
    print('Result:', chat_res.answer if hasattr(chat_res, 'answer') else chat_res)
    print('-' * 60)

    # 3️⃣ Ayurvedic query
    print('Step 3: Ayurvedic Query – Stress Relief')
    ayur_res = await client.chat('What Ayurvedic practices can help me reduce stress and improve sleep?')
    print('Result:', ayur_res.answer if hasattr(ayur_res, 'answer') else ayur_res)
    print('-' * 60)

    # 4️⃣ Autopilot – Booking intent
    print('Step 4: Autopilot – Booking Intent')
    autopilot_res = await client.autopilot('I need to book a physiotherapy session for my lower back pain next week.')
    print('Result:', autopilot_res)
    print('-' * 60)

    # 5️⃣ Smart Prescription – Schedule parsing
    print('Step 5: Smart Prescription – Medication Schedule')
    rx_text = "Tab. Ibuprofen 400mg - 1-0-1 after food for 5 days. SYP. Ashwagandha 10ml BID."
    presc_res = await client.extract_schedule(rx_text)
    print('Result:', json.dumps(presc_res, indent=2) if isinstance(presc_res, dict) else presc_res)
    print('-' * 60)

    # 6️⃣ Wellness – Meditation generation
    print('Step 6: Wellness – Meditation Script')
    med_res = await client.generate_wellness('10‑minute bedtime meditation for anxiety relief', '10 mins')
    print('Result:', json.dumps(med_res, indent=2) if isinstance(med_res, dict) else med_res)
    print('-' * 60)

    # 7️⃣ Wellness – Yoga plan generation
    print('Step 7: Wellness – Yoga Plan')
    yoga_res = await client.generate_wellness('Yoga sequence for lower back pain', '15 mins')
    print('Result:', json.dumps(yoga_res, indent=2) if isinstance(yoga_res, dict) else yoga_res)
    print('-' * 60)

    # 8️⃣ AutoCart – Product mapping (Shop Assist)
    print('Step 8: AutoCart – Product Recommendations')
    shop_res = await client.shop_assist('I need natural remedies for chronic lower back pain.')
    print('Result:', json.dumps(shop_res, indent=2) if isinstance(shop_res, dict) else shop_res)
    print('-' * 60)

    # 9️⃣ Clinical – Doctor summary
    print('Step 9: Clinical – Doctor Summary')
    patient_notes = "Patient: 34F. Complaints: lower back pain, occasional right‑leg numbness, insomnia. Lifestyle: high stress, vegetarian diet."
    clinical_res = await client.doctor_summary(patient_notes)
    print('Result:', json.dumps(clinical_res, indent=2) if isinstance(clinical_res, dict) else clinical_res)
    print('-' * 60)

    # 🔟 Safety check
    print('Step 10: Safety – Risk Assessment')
    safety_res = await client.analyze_safety('I feel very stressed and sometimes think about harming myself.')
    print('Result:', json.dumps(safety_res, indent=2) if isinstance(safety_res, dict) else safety_res)
    print('-' * 60)

    # 1️⃣1️⃣ Emotion detection
    print('Step 11: Emotion – Detection')
    emotion_res = await client.detect_emotion('I am excited about starting a new yoga practice tomorrow!')
    print('Result:', json.dumps(emotion_res, indent=2) if isinstance(emotion_res, dict) else emotion_res)
    print('-' * 60)

    # 1️⃣2️⃣ Social – Buddy matching
    print('Step 12: Social – Buddy Matching')
    p_a = '{"interests": ["Yoga", "Meditation"], "goals": ["Stress reduction"]}'
    p_b = '{"interests": ["Yoga", "Running"], "goals": ["Fitness"]}'
    social_res = await client.profile_analysis(p_a, "buddy_match", p_b)
    print('Result:', json.dumps(social_res, indent=2) if isinstance(social_res, dict) else social_res)
    print('-' * 60)

    await client.close()
    print('\n=== End of Mock Patient Journey ===\n')

if __name__ == '__main__':
    asyncio.run(mock_patient_flow())
