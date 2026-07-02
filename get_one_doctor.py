"""
Test script to retrieve one real doctor from the service
"""
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.doctors.doctor_service import doctor_service

async def get_one_doctor():
    print("=" * 60)
    print("RETRIEVING ONE DOCTOR FROM DOCTOR SERVICE")
    print("=" * 60)
    
    # Get all doctors (will use mock data if DB not accessible)
    doctors = await doctor_service.get_all_doctors(limit=1)
    
    if doctors:
        doctor = doctors[0]
        print("\n✅ Successfully retrieved doctor:\n")
        print(f"  👨‍⚕️ Name: {doctor['name']}")
        print(f"  🏥 Specialization: {doctor['specialization']}")
        print(f"  📅 Experience: {doctor['experience_years']} years")
        print(f"  💰 Consultation Fee: ₹{doctor['consultation_fee']}")
        print(f"  📍 Location: {doctor['location']}")
        print(f"  🆔 Doctor ID: {doctor['doctor_id']}")
        print("\n" + "=" * 60)
        return doctor
    else:
        print("\n❌ No doctors found")
        print("=" * 60)
        return None

if __name__ == "__main__":
    asyncio.run(get_one_doctor())
