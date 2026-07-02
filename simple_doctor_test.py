"""
Simple synchronous test to get one doctor
"""
import sys
import os

sys.path.append(os.getcwd())

from app.doctors.mock_doctor_data import get_mock_doctors

def main():
    print("=" * 60)
    print("RETRIEVING ONE DOCTOR")
    print("=" * 60)
    
    doctors = get_mock_doctors(limit=1)
    
    if doctors:
        doctor = doctors[0]
        print("\n✅ Successfully retrieved doctor:\n")
        print(f"  👨‍⚕️ Name: {doctor['name']}")
        print(f"  🏥 Specialization: {doctor['specialization']}")
        print(f"  📅 Experience: {doctor['experience_years']} years")
        print(f"  💰 Consultation Fee: ₹{doctor['consultation_fee']}")
        print(f"  📍 Location: {doctor['location']}")
        print(f"  🆔 Doctor ID: {doctor['doctor_id']}")
        
        if 'qualifications' in doctor:
            print(f"  🎓 Qualifications: {', '.join(doctor['qualifications'])}")
        if 'languages' in doctor:
            print(f"  🗣️ Languages: {', '.join(doctor['languages'])}")
        if 'bio' in doctor:
            print(f"  📝 Bio: {doctor['bio']}")
        
        print("\n" + "=" * 60)
        return doctor
    else:
        print("\n❌ No doctors found")
        print("=" * 60)
        return None

if __name__ == "__main__":
    main()
