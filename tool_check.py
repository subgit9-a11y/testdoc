import asyncio
import logging
import sys
import os

# Set path
sys.path.append("c:/Users/SUBHASH/Desktop/vultr_astra_1.0")

from app.astra.tool_registry import tool_registry

async def check_tools():
    print("--- MINIMAL TOOL CHECK START ---")
    
    # Test Shopify Search
    try:
        print("Testing Shopify Search...")
        result = await tool_registry.execute("shopify_search", {"query": "Ashwagandha"})
        print(f"Shopify Result: {str(result)[:100]}")
    except Exception as e:
        print(f"Shopify Error: {e}")

    # Test Doctor Search
    try:
        print("Testing Doctor Search...")
        result = await tool_registry.execute("doctor_search", {"specialization": "Ayurveda"})
        print(f"Doctor Result: {str(result)[:100]}")
    except Exception as e:
        print(f"Doctor Error: {e}")

    print("--- MINIMAL TOOL CHECK END ---")

if __name__ == "__main__":
    asyncio.run(check_tools())
