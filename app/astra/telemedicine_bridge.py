"""
Telemedicine Bridge - Smart Doctor Escalation System

Intelligently connects users to real doctors when AI cannot help.

FEATURES:
- Automatic escalation detection
- Doctor matching algorithm
- Pre-consultation summary generation
- Appointment scheduling
- Follow-up automation
- Video consultation integration

ESCALATION TRIGGERS:
- CLASS_C or CLASS_D intents (forbidden/emergency)
- User explicitly requests doctor
- Symptoms persist beyond threshold
- Complex medical queries
- Medication side effects
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EscalationReason(Enum):
    """Reasons for escalating to doctor"""
    EMERGENCY = "emergency"
    FORBIDDEN_CAPABILITY = "forbidden_capability"
    USER_REQUEST = "user_request"
    PERSISTENT_SYMPTOMS = "persistent_symptoms"
    COMPLEX_QUERY = "complex_query"
    MEDICATION_CONCERN = "medication_concern"
    SECOND_OPINION = "second_opinion"


class DoctorSpecialization(Enum):
    """Doctor specializations"""
    GENERAL_AYURVEDA = "general_ayurveda"
    PANCHAKARMA = "panchakarma"
    RASAYANA = "rasayana"
    KAYACHIKITSA = "kayachikitsa"  # Internal medicine
    SHALYA_TANTRA = "shalya_tantra"  # Surgery
    SHALAKYA_TANTRA = "shalakya_tantra"  # ENT, Eye
    PRASUTI_TANTRA = "prasuti_tantra"  # Gynecology
    KAUMARA_BHRITYA = "kaumara_bhritya"  # Pediatrics


@dataclass
class DoctorProfile:
    """Doctor profile information"""
    doctor_id: str
    name: str
    specialization: DoctorSpecialization
    qualifications: List[str]
    experience_years: int
    languages: List[str]
    rating: float
    consultation_fee: float
    available_slots: List[datetime]
    is_verified: bool
    location: str


@dataclass
class EscalationRequest:
    """Escalation request data"""
    request_id: str
    user_id: str
    profile_id: str
    reason: EscalationReason
    urgency: str  # "low", "medium", "high", "critical"
    user_query: str
    conversation_history: List[Dict]
    symptoms: List[str]
    duration: Optional[str]
    preferred_language: str
    created_at: datetime


@dataclass
class PreConsultationSummary:
    """AI-generated summary for doctor"""
    summary_id: str
    patient_name: str
    age: int
    gender: str
    chief_complaint: str
    symptoms: List[str]
    symptom_duration: str
    previous_consultations: int
    current_medications: List[str]
    allergies: List[str]
    dosha_assessment: Optional[str]
    ai_conversation_summary: str
    red_flags: List[str]
    suggested_focus_areas: List[str]


class TelemedicineBridge:
    """
    Smart bridge between AI and human doctors.
    
    Handles:
    - Escalation detection
    - Doctor matching
    - Appointment booking
    - Pre-consultation summaries
    - Follow-up automation
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize telemedicine bridge.
        
        Args:
            db_connection: Database connection
        """
        self.db = db_connection
        self.escalation_rules = self._load_escalation_rules()
        
        logger.info("✅ Telemedicine Bridge initialized")
    
    def _load_escalation_rules(self) -> Dict:
        """Load escalation rules"""
        return {
            "emergency_keywords": [
                "emergency", "urgent", "severe pain", "chest pain",
                "can't breathe", "bleeding", "unconscious", "seizure"
            ],
            "symptom_duration_threshold_days": 7,
            "max_ai_attempts": 3,
            "forbidden_intent_classes": ["CLASS_C", "CLASS_D"]
        }
    
    async def should_escalate(
        self,
        user_query: str,
        intent_class: str,
        conversation_history: List[Dict],
        symptoms: Optional[List[str]] = None
    ) -> Dict:
        """
        Determine if query should be escalated to doctor.
        
        Args:
            user_query: User's query
            intent_class: Detected intent class
            conversation_history: Recent conversation
            symptoms: List of symptoms (if any)
        
        Returns:
            {
                "should_escalate": bool,
                "reason": EscalationReason,
                "urgency": str,
                "explanation": str
            }
        """
        # Rule 1: Emergency detection (CLASS_D)
        if intent_class == "CLASS_D":
            return {
                "should_escalate": True,
                "reason": EscalationReason.EMERGENCY,
                "urgency": "critical",
                "explanation": "Emergency keywords detected. Immediate medical attention required."
            }
        
        # Rule 2: Forbidden capability (CLASS_C)
        if intent_class == "CLASS_C":
            return {
                "should_escalate": True,
                "reason": EscalationReason.FORBIDDEN_CAPABILITY,
                "urgency": "high",
                "explanation": "This query requires professional medical consultation."
            }
        
        # Rule 3: User explicitly requests doctor
        if self._user_requests_doctor(user_query):
            return {
                "should_escalate": True,
                "reason": EscalationReason.USER_REQUEST,
                "urgency": "medium",
                "explanation": "User requested to speak with a doctor."
            }
        
        # Rule 4: Persistent symptoms
        if symptoms and len(symptoms) > 0:
            if self._symptoms_persistent(conversation_history):
                return {
                    "should_escalate": True,
                    "reason": EscalationReason.PERSISTENT_SYMPTOMS,
                    "urgency": "medium",
                    "explanation": "Symptoms have persisted. Professional evaluation recommended."
                }
        
        # Rule 5: Complex medical query
        if self._is_complex_query(user_query):
            return {
                "should_escalate": True,
                "reason": EscalationReason.COMPLEX_QUERY,
                "urgency": "medium",
                "explanation": "This query is complex and requires professional medical expertise."
            }
        
        # No escalation needed
        return {
            "should_escalate": False,
            "reason": None,
            "urgency": "low",
            "explanation": "AI can handle this query."
        }
    
    def _user_requests_doctor(self, query: str) -> bool:
        """Check if user explicitly requests doctor"""
        doctor_keywords = [
            "talk to doctor", "speak to doctor", "consult doctor",
            "see a doctor", "doctor appointment", "need a doctor",
            "human doctor", "real doctor"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in doctor_keywords)
    
    def _symptoms_persistent(self, conversation_history: List[Dict]) -> bool:
        """Check if symptoms have been mentioned repeatedly"""
        # Count symptom mentions in last N messages
        symptom_mentions = 0
        for msg in conversation_history[-10:]:  # Last 10 messages
            if "symptom" in msg.get("message", "").lower():
                symptom_mentions += 1
        
        return symptom_mentions >= 3
    
    def _is_complex_query(self, query: str) -> bool:
        """Detect complex medical queries"""
        complex_indicators = [
            "diagnosis", "treatment plan", "surgery", "operation",
            "medication dosage", "drug interaction", "side effect",
            "chronic condition", "serious illness"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complex_indicators)
    
    async def find_matching_doctors(
        self,
        specialization: Optional[DoctorSpecialization] = None,
        language: str = "en",
        location: Optional[str] = None,
        max_results: int = 5
    ) -> List[DoctorProfile]:
        """
        Find doctors matching criteria.
        
        Args:
            specialization: Required specialization
            language: Preferred language
            location: User location
            max_results: Maximum results to return
        
        Returns:
            List of matching DoctorProfile objects
        """
        if not self.db:
            # Return mock data for demonstration
            return [
                DoctorProfile(
                    doctor_id="doc_001",
                    name="Dr. Priya Sharma",
                    specialization=DoctorSpecialization.GENERAL_AYURVEDA,
                    qualifications=["BAMS", "MD (Ayurveda)"],
                    experience_years=12,
                    languages=["English", "Hindi", "Tamil"],
                    rating=4.8,
                    consultation_fee=500.0,
                    available_slots=[
                        datetime.utcnow() + timedelta(hours=2),
                        datetime.utcnow() + timedelta(days=1)
                    ],
                    is_verified=True,
                    location="Mumbai"
                ),
                DoctorProfile(
                    doctor_id="doc_002",
                    name="Dr. Rajesh Kumar",
                    specialization=DoctorSpecialization.KAYACHIKITSA,
                    qualifications=["BAMS", "MD (Kayachikitsa)"],
                    experience_years=15,
                    languages=["English", "Hindi"],
                    rating=4.9,
                    consultation_fee=600.0,
                    available_slots=[
                        datetime.utcnow() + timedelta(hours=4),
                        datetime.utcnow() + timedelta(days=1, hours=2)
                    ],
                    is_verified=True,
                    location="Delhi"
                )
            ]
        
        # Query database for doctors
        # Implementation depends on your database schema
        return []
    
    async def generate_pre_consultation_summary(
        self,
        user_id: str,
        profile_id: str,
        conversation_history: List[Dict],
        symptoms: List[str]
    ) -> PreConsultationSummary:
        """
        Generate AI-powered pre-consultation summary for doctor.
        
        Args:
            user_id: User ID
            profile_id: Profile ID
            conversation_history: Recent conversation
            symptoms: Reported symptoms
        
        Returns:
            PreConsultationSummary object
        """
        import uuid
        
        # Extract key information from conversation
        chief_complaint = self._extract_chief_complaint(conversation_history)
        symptom_duration = self._estimate_symptom_duration(conversation_history)
        red_flags = self._identify_red_flags(symptoms, conversation_history)
        
        # Get user profile data
        patient_data = await self._get_patient_data(user_id, profile_id)
        
        # Generate conversation summary
        ai_summary = self._summarize_conversation(conversation_history)
        
        # Suggest focus areas for doctor
        focus_areas = self._suggest_focus_areas(symptoms, conversation_history)
        
        summary = PreConsultationSummary(
            summary_id=str(uuid.uuid4()),
            patient_name=patient_data.get("name", "Patient"),
            age=patient_data.get("age", 0),
            gender=patient_data.get("gender", "Not specified"),
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            symptom_duration=symptom_duration,
            previous_consultations=patient_data.get("consultation_count", 0),
            current_medications=patient_data.get("medications", []),
            allergies=patient_data.get("allergies", []),
            dosha_assessment=patient_data.get("dosha", None),
            ai_conversation_summary=ai_summary,
            red_flags=red_flags,
            suggested_focus_areas=focus_areas
        )
        
        logger.info(f"✅ Generated pre-consultation summary: {summary.summary_id}")
        return summary
    
    def _extract_chief_complaint(self, conversation: List[Dict]) -> str:
        """Extract main complaint from conversation"""
        # Simple extraction - first user message
        for msg in conversation:
            if msg.get("role") == "user":
                return msg.get("message", "General consultation")[:200]
        return "General consultation"
    
    def _estimate_symptom_duration(self, conversation: List[Dict]) -> str:
        """Estimate how long symptoms have been present"""
        duration_keywords = {
            "today": "Less than 1 day",
            "yesterday": "1-2 days",
            "few days": "3-7 days",
            "week": "1-2 weeks",
            "weeks": "2-4 weeks",
            "month": "1-3 months",
            "months": "3+ months"
        }
        
        for msg in conversation:
            message_text = msg.get("message", "").lower()
            for keyword, duration in duration_keywords.items():
                if keyword in message_text:
                    return duration
        
        return "Duration not specified"
    
    def _identify_red_flags(self, symptoms: List[str], conversation: List[Dict]) -> List[str]:
        """Identify concerning symptoms"""
        red_flag_keywords = [
            "severe pain", "chest pain", "difficulty breathing",
            "bleeding", "high fever", "unconscious", "seizure",
            "sudden weakness", "vision loss", "severe headache"
        ]
        
        red_flags = []
        all_text = " ".join([msg.get("message", "") for msg in conversation]).lower()
        
        for flag in red_flag_keywords:
            if flag in all_text:
                red_flags.append(flag.title())
        
        return red_flags
    
    def _summarize_conversation(self, conversation: List[Dict]) -> str:
        """Create concise summary of AI conversation"""
        # Simple summary - last 5 exchanges
        summary_parts = []
        for msg in conversation[-10:]:
            role = "Patient" if msg.get("role") == "user" else "Astra AI"
            text = msg.get("message", "")[:100]
            summary_parts.append(f"{role}: {text}")
        
        return "\n".join(summary_parts)
    
    def _suggest_focus_areas(self, symptoms: List[str], conversation: List[Dict]) -> List[str]:
        """Suggest areas for doctor to focus on"""
        focus_areas = []
        
        # Based on symptoms
        if any("pain" in s.lower() for s in symptoms):
            focus_areas.append("Pain assessment and management")
        
        if any("digestive" in s.lower() or "stomach" in s.lower() for s in symptoms):
            focus_areas.append("Digestive system evaluation")
        
        if any("stress" in s.lower() or "anxiety" in s.lower() for s in symptoms):
            focus_areas.append("Mental health and stress management")
        
        # Default
        if not focus_areas:
            focus_areas.append("Comprehensive Ayurvedic assessment")
        
        return focus_areas
    
    async def _get_patient_data(self, user_id: str, profile_id: str) -> Dict:
        """Get patient data from database"""
        if not self.db:
            return {
                "name": "Patient",
                "age": 35,
                "gender": "Not specified",
                "consultation_count": 0,
                "medications": [],
                "allergies": [],
                "dosha": None
            }
        
        # Query database
        # Implementation depends on your schema
        return {}
    
    async def book_appointment(
        self,
        user_id: str,
        profile_id: str,
        doctor_id: str,
        slot_time: datetime,
        consultation_type: str = "video"
    ) -> Dict:
        """
        Book appointment with doctor.
        
        Args:
            user_id: User ID
            profile_id: Profile ID
            doctor_id: Doctor ID
            slot_time: Appointment time
            consultation_type: "video", "audio", or "chat"
        
        Returns:
            {
                "success": bool,
                "appointment_id": str,
                "doctor_name": str,
                "scheduled_time": datetime,
                "meeting_link": str
            }
        """
        import uuid
        
        appointment_id = str(uuid.uuid4())
        
        # Create appointment in database
        if self.db:
            # Save appointment
            pass
        
        # Generate meeting link (integrate with video platform)
        meeting_link = f"https://meet.ayureze.in/{appointment_id}"
        
        # Send confirmation notifications
        await self._send_appointment_confirmation(
            user_id, doctor_id, appointment_id, slot_time, meeting_link
        )
        
        logger.info(f"✅ Appointment booked: {appointment_id}")
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "doctor_name": "Dr. Sharma",  # Fetch from DB
            "scheduled_time": slot_time.isoformat(),
            "meeting_link": meeting_link,
            "consultation_type": consultation_type
        }
    
    async def _send_appointment_confirmation(
        self,
        user_id: str,
        doctor_id: str,
        appointment_id: str,
        slot_time: datetime,
        meeting_link: str
    ):
        """Send appointment confirmation to user and doctor"""
        # Send push notification
        # Send WhatsApp message
        # Send email
        # Add to calendar
        pass
    
    async def create_escalation_request(
        self,
        user_id: str,
        profile_id: str,
        reason: EscalationReason,
        urgency: str,
        user_query: str,
        conversation_history: List[Dict],
        symptoms: List[str]
    ) -> EscalationRequest:
        """
        Create escalation request.
        
        Args:
            user_id: User ID
            profile_id: Profile ID
            reason: Escalation reason
            urgency: Urgency level
            user_query: User's query
            conversation_history: Conversation history
            symptoms: Symptoms list
        
        Returns:
            EscalationRequest object
        """
        import uuid
        
        request = EscalationRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            profile_id=profile_id,
            reason=reason,
            urgency=urgency,
            user_query=user_query,
            conversation_history=conversation_history,
            symptoms=symptoms,
            duration=self._estimate_symptom_duration(conversation_history),
            preferred_language="en",
            created_at=datetime.utcnow()
        )
        
        # Save to database
        if self.db:
            # Save escalation request
            pass
        
        logger.info(f"✅ Escalation request created: {request.request_id} (urgency: {urgency})")
        return request
