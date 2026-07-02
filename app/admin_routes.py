from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import the database managers
from app.database import db_manager # Supabase Database
from app.database_models import get_db # MySQL Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Superadmin Panel"])

@router.get("/dashboard-stats")
async def get_superadmin_dashboard_stats(db: Session = Depends(get_db)):
    """
    Fetches unified dashboard statistics combining MySQL (Users, Doctors) 
    and Supabase (Astra Cases, EHR).
    """
    try:
        stats = {
            "mysql": {
                "total_patients": 0,
                "total_doctors": 0,
            },
            "supabase": {
                "total_health_cases": 0,
                "total_prescriptions": 0,
            }
        }
        
        # 1. Fetch from MySQL (Core App)
        try:
            # Safely query MySQL tables if they exist
            patients_count = db.execute(text("SELECT COUNT(*) FROM patient_profiles")).scalar()
            doctors_count = db.execute(text("SELECT COUNT(*) FROM doctor_profiles")).scalar()
            
            stats["mysql"]["total_patients"] = patients_count or 0
            stats["mysql"]["total_doctors"] = doctors_count or 0
        except Exception as e:
            logger.warning(f"Could not fetch MySQL stats: {e}")
            
        # 2. Fetch from Supabase (Astra AI)
        if db_manager.is_connected():
            try:
                cases_res = db_manager.client.table("health_cases").select("count", count="exact").execute()
                prescriptions_res = db_manager.client.table("prescription_records").select("count", count="exact").execute()
                
                stats["supabase"]["total_health_cases"] = cases_res.count if cases_res.count else 0
                stats["supabase"]["total_prescriptions"] = prescriptions_res.count if prescriptions_res.count else 0
            except Exception as e:
                logger.warning(f"Could not fetch Supabase stats: {e}")
                
        # 3. Calculate Combined Metrics
        combined = {
            "total_users": stats["mysql"]["total_patients"] + stats["mysql"]["total_doctors"],
            "total_ai_cases": stats["supabase"]["total_health_cases"],
            "total_prescriptions": stats["supabase"]["total_prescriptions"],
            "raw_data": stats
        }
        
        return {
            "success": True,
            "data": combined
        }
        
    except Exception as e:
        logger.error(f"Error fetching superadmin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients")
async def get_superadmin_patients():
    """
    Fetches the patient directory and their EHR vault status from Supabase.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Supabase not connected")
        
    try:
        # Fetch patients from Supabase
        patients_res = db_manager.client.table("patient_profiles").select("*").execute()
        patients = patients_res.data if patients_res.data else []
        
        # We also want to know how many health cases and EHR documents each has
        for p in patients:
            pid = p.get("patient_id")
            if not pid:
                continue
                
            # Count cases
            cases_res = db_manager.client.table("health_cases").select("count", count="exact").eq("user_id", pid).execute()
            p["total_cases"] = cases_res.count if cases_res.count else 0
            
            # Count EHR documents
            docs_res = db_manager.client.table("documents").select("count", count="exact").eq("patient_id", pid).execute()
            p["total_ehr_docs"] = docs_res.count if docs_res.count else 0
            
            # Get latest case progress if any
            if p["total_cases"] > 0:
                latest_case = db_manager.client.table("health_cases").select("*").eq("user_id", pid).order("created_at", desc=True).limit(1).execute()
                if latest_case.data:
                    p["latest_case_progress"] = latest_case.data[0].get("progress_percentage", 0)
                    p["latest_case_status"] = latest_case.data[0].get("status", "active")
        
        return {
            "success": True,
            "data": patients
        }
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- DOCTOR MANAGEMENT ENDPOINTS ---

@router.get("/doctors")
async def get_superadmin_doctors(db: Session = Depends(get_db)):
    """
    Fetches doctors from MySQL and their wallet balances.
    """
    try:
        # Fetch doctors from MySQL
        doctors = []
        try:
            res = db.execute(text("SELECT id, doctor_id, name, email, phone, specialization, is_active, is_verified, consultation_fee FROM doctor_profiles")).mappings().all()
            for doc in res:
                doc_dict = dict(doc)
                # Fetch wallet
                wallet_res = db.execute(text("SELECT total_earned, available_balance, withdrawn_amount FROM doctor_wallets WHERE doctor_id = :did"), {"did": doc_dict["doctor_id"]}).mappings().first()
                if wallet_res:
                    doc_dict.update(dict(wallet_res))
                else:
                    doc_dict.update({"total_earned": 0, "available_balance": 0, "withdrawn_amount": 0})
                doctors.append(doc_dict)
        except Exception as e:
            logger.warning(f"Could not fetch MySQL doctors: {e}")

        return {
            "success": True,
            "data": doctors
        }
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctors/{doctor_id}/toggle-verify")
async def toggle_doctor_verification(doctor_id: str, db: Session = Depends(get_db)):
    """Toggle doctor verification status"""
    try:
        db.execute(
            text("UPDATE doctor_profiles SET is_verified = NOT is_verified WHERE doctor_id = :did"),
            {"did": doctor_id}
        )
        db.commit()
        return {"success": True, "message": "Verification toggled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# --- AI CONTROL CENTER ENDPOINTS ---

@router.get("/ai/journeys")
async def get_superadmin_ai_journeys():
    """
    Fetches all active AI Autopilot journeys from Supabase.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Supabase not connected")
        
    try:
        # Fetch patient care states
        res = db_manager.client.table("patient_care_states").select("*").execute()
        return {
            "success": True,
            "data": res.data if res.data else []
        }
    except Exception as e:
        logger.error(f"Error fetching AI journeys: {e}")
        raise HTTPException(status_code=500, detail=str(e))
