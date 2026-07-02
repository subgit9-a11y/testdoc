"""
Mock Doctor Data for Testing
This provides sample doctor data when the database is not accessible
"""

MOCK_DOCTORS = [
    {
        "doctor_id": "doc_001",
        "name": "Dr. Rajesh Kumar",
        "specialization": "Ayurveda Specialist",
        "experience_years": 15,
        "consultation_fee": 800,
        "location": "Bangalore",
        "qualifications": ["BAMS", "MD Ayurveda"],
        "languages": ["English", "Hindi", "Kannada"],
        "available_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
        "bio": "Specialized in Panchakarma therapy and stress management"
    },
    {
        "doctor_id": "doc_002",
        "name": "Dr. Priya Sharma",
        "specialization": "General Physician",
        "experience_years": 10,
        "consultation_fee": 600,
        "location": "Mumbai",
        "qualifications": ["MBBS", "MD"],
        "languages": ["English", "Hindi", "Marathi"],
        "available_days": ["Monday", "Wednesday", "Thursday", "Saturday"],
        "bio": "Expert in preventive healthcare and lifestyle diseases"
    },
    {
        "doctor_id": "doc_003",
        "name": "Dr. Arun Patel",
        "specialization": "Ayurveda Specialist",
        "experience_years": 12,
        "consultation_fee": 700,
        "location": "Delhi",
        "qualifications": ["BAMS", "PhD Ayurveda"],
        "languages": ["English", "Hindi", "Gujarati"],
        "available_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "bio": "Specialized in digestive disorders and immunity building"
    },
    {
        "doctor_id": "doc_004",
        "name": "Dr. Meera Reddy",
        "specialization": "Dermatologist",
        "experience_years": 8,
        "consultation_fee": 900,
        "location": "Hyderabad",
        "qualifications": ["MBBS", "MD Dermatology"],
        "languages": ["English", "Telugu", "Hindi"],
        "available_days": ["Monday", "Tuesday", "Friday", "Saturday"],
        "bio": "Expert in skin and hair care with Ayurvedic approach"
    },
    {
        "doctor_id": "doc_005",
        "name": "Dr. Vikram Singh",
        "specialization": "Orthopedic Specialist",
        "experience_years": 20,
        "consultation_fee": 1000,
        "location": "Chennai",
        "qualifications": ["MBBS", "MS Orthopedics"],
        "languages": ["English", "Tamil", "Hindi"],
        "available_days": ["Monday", "Wednesday", "Thursday", "Friday"],
        "bio": "Specialized in joint pain and sports injuries"
    }
]

def get_mock_doctors(specialization=None, limit=5):
    """Get mock doctor data with optional filtering"""
    doctors = MOCK_DOCTORS
    
    if specialization:
        doctors = [
            d for d in doctors 
            if specialization.lower() in d["specialization"].lower()
        ]
    
    return doctors[:limit]

def get_mock_doctor_by_id(doctor_id):
    """Get a specific mock doctor by ID"""
    for doctor in MOCK_DOCTORS:
        if doctor["doctor_id"] == doctor_id:
            return doctor
    return None
