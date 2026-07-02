import asyncio
import logging
import sys
import os

# Set PYTHONPATH
sys.path.append(os.getcwd())

from app.doctors.doctor_service import doctor_service

logging.basicConfig(level=logging.INFO)

async def test_get_doctors():
    print("Fetching doctors from DoctorService...")
    doctors = await doctor_service.get_all_doctors(limit=10)
    print(f"Result: {doctors}")
    
    if not doctors:
        print("No doctors found. Checking if search works...")
        # Try a generic search if any search method exists that doesn't require lat/lon
        pass

if __name__ == "__main__":
    asyncio.run(test_get_doctors())
