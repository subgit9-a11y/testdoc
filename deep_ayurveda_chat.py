
import asyncio
import os
import json
import httpx
from typing import List

# Import the actual client used by the app
try:
    if os.path.exists(".env.txt"):
        with open(".env.txt", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val
    
    from app.astra_brain_client import AstraBrainClient
except ImportError:
    print("Error: Could not import app modules.")
    exit(1)

async def deep_chat_demo():
    client = AstraBrainClient()
    # Ensure long timeout for deep responses
    client.client.timeout = httpx.Timeout(300.0, read=300.0, connect=10.0)
    
    questions = [
        "How can I balance my Pitta dosha during the summer heat? Provide deep Ayurvedic wisdom on food, lifestyle, and herbs.",
        "What is the significance of Ojas in Ayurveda, and how can I build it to increase your vitality and immunity?",
        "I feel mental fog and low energy. Can you explain the concept of Agni and Ama in this context and provide a solution?",
        "My skin feels dry and itchy during winter. What Ayurvedic regimen can restore moisture and calm Vata?",
        "I have frequent heartburn after meals. Which Ayurvedic dietary and lifestyle adjustments can soothe Pitta and improve digestion?",
        "I struggle with insomnia and restless thoughts at night. How can I use Ayurvedic practices to calm the mind and promote deep sleep?"
    ]
    
    print("\n--- Deep Ayurvedic AI Demo ---\n")
    
    for q in questions:
        print(f"USER: {q}")
        print("-" * 30)
        print("ASTRA AI: Generating deep response...", flush=True)
        
        result = await client.chat(q)
        if result.success:
            print(f"\n{result.answer}\n")
        else:
            print(f"Error: {result.answer}")
        
        print("=" * 60 + "\n")
        
    await client.close()

if __name__ == "__main__":
    asyncio.run(deep_chat_demo())
