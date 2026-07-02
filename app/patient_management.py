"""
Patient Management API (Supabase Powered)
Handles patient registration, search, and doctor-patient linking via Supabase.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import logging
import json
import uuid

from app.database import db_manager
from app.firebase_auth_middleware import require_firebase_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["Patient Management"])

class PatientRegistration(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []

@router.post("/register")
async def register_patient(
    patient_data: PatientRegistration,
    user_token: Dict[str, Any] = Depends(require_firebase_auth)
):
    """Register a new patient using Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        patient_id = user_token["user_id"]
        
        # Check existing
        existing = await db_manager.get_patient_profile(patient_id)
        if existing:
            return {"success": True, "patient_id": patient_id, "is_existing": True, "data": existing}

        # Create new profile
        patient_code = f"P-{uuid.uuid4().hex[:6].upper()}"
        new_profile = {
            "patient_id": patient_id,
            "patient_code": patient_code,
            "name": patient_data.name,
            "email": patient_data.email or user_token.get("email"),
            "phone": patient_data.phone or user_token.get("phone_number"),
            "age": patient_data.age,
            "gender": patient_data.gender,
            "address": patient_data.address,
            "medical_conditions": patient_data.medical_conditions,
            "allergies": patient_data.allergies,
            "is_active": True
        }
        
        res = db_manager.client.table("patient_profiles").insert(new_profile).execute()
        
        return {"success": True, "patient_id": patient_id, "patient_code": patient_code, "data": res.data[0]}
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify/{patient_code}")
async def verify_patient_code(patient_code: str):
    """Verify patient by code against Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        res = db_manager.client.table("patient_profiles").select("*").eq("patient_code", patient_code.upper()).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return res.data[0]
    except HTTPException: raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{patient_id}")
async def get_patient_profile(patient_id: str):
    """Get profile from Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    profile = await db_manager.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@router.get("/search/{search_term}", response_model=List[Dict[str, Any]])
async def search_patients(search_term: str):
    """Search patients by name, phone, or code in Supabase"""
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not available")
    
    results = await db_manager.search_patients(search_term)
    return results
