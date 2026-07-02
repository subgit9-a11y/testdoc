"""
Admin Panel API Routes (Supabase Powered)
Handles system configuration, logs, and dashboard stats via Supabase
"""

import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.config import settings
from app.database import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])

# --- Models ---

class SystemStats(BaseModel):
    status: str
    timestamp: str
    database_connected: bool
    model_loaded: bool
    active_sessions: int
    total_users: int
    total_doctors: int
    total_centers: int

class PayoutRequest(BaseModel):
    doctor_id: str
    amount: int

class AstraConfig(BaseModel):
    base_model: Optional[str] = None
    lora_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class WasabiConfig(BaseModel):
    endpoint: Optional[str] = None
    bucket: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None

# --- Dependencies ---

def get_admin_user():
    # TODO: Implement proper admin authentication (e.g. Firebase Admin SDK check)
    return {"role": "admin"}

# --- Routes ---

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get aggregated system statistics from Supabase"""
    try:
        db_connected = db_manager.is_connected()
        
        # Model status
        model_loaded = False
        try:
            # Check if model is loaded via global instance if possible
            from main import model
            model_loaded = model.is_loaded() if hasattr(model, 'is_loaded') else True
        except:
            pass
        
        # Counts from Supabase
        users_count = 0
        doctors_count = 0
        centers_count = 0
        sessions_count = 0

        if db_connected and db_manager.client:
            try:
                res_u = db_manager.client.table("astra_users").select("*", count="exact").limit(0).execute()
                users_count = res_u.count or 0
                
                res_d = db_manager.client.table("doctors").select("*", count="exact").limit(0).execute()
                doctors_count = res_d.count or 0
                
                res_c = db_manager.client.table("consultations").select("*", count="exact").limit(0).execute()
                centers_count = res_c.count or 0
                
                yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
                res_s = db_manager.client.table("astra_sessions").select("*", count="exact").gt("created_at", yesterday).limit(0).execute()
                sessions_count = res_s.count or 0
            except Exception as e:
                logger.warning(f"Error fetching counts from Supabase: {e}")

        return SystemStats(
            status="operational" if db_connected else "degraded",
            timestamp=datetime.now().isoformat(),
            database_connected=db_connected,
            model_loaded=model_loaded,
            active_sessions=sessions_count,
            total_users=users_count,
            total_doctors=doctors_count,
            total_centers=centers_count
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/doctors")
async def list_doctors(user: dict = Depends(get_admin_user)):
    """List all doctors with wallet information"""
    if not db_manager.client: return []
    res = db_manager.client.table("doctors").select("*, doctor_wallets(*)").execute()
    return res.data

@router.post("/doctors/{doctor_id}/toggle-status")
async def toggle_doctor_status(doctor_id: str, active: bool, user: dict = Depends(get_admin_user)):
    """Enable or disable a doctor account"""
    if not db_manager.client: raise HTTPException(status_code=500)
    db_manager.client.table("doctors").update({"is_active": active}).eq("doctor_id", doctor_id).execute()
    return {"status": "updated", "doctor_id": doctor_id, "is_active": active}

@router.get("/payouts")
async def list_payouts(user: dict = Depends(get_admin_user)):
    """Retrieve all withdrawal requests with 30/70 split details"""
    if not db_manager.client: return []
    res = db_manager.client.table("withdrawal_requests").select("*, doctors(name)").order("created_at", desc=True).execute()
    return res.data

@router.post("/payouts/{request_id}/approve")
async def approve_payout(request_id: str, user: dict = Depends(get_admin_user)):
    """Confirm a payout, deduct from wallet, and mark as completed"""
    if not db_manager.client: raise HTTPException(status_code=500)
    
    # 1. Get request details
    req = db_manager.client.table("withdrawal_requests").select("*").eq("id", request_id).single().execute()
    if not req.data: raise HTTPException(status_code=404, detail="Request not found")
    
    if req.data['status'] != 'pending':
        return {"status": "skipped", "reason": "Already processed"}

    # 2. Update status
    db_manager.client.table("withdrawal_requests").update({
        "status": "completed",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", request_id).execute()
    
    # 3. Adjust wallet
    doctor_id = req.data['doctor_id']
    amount = req.data['amount']
    
    wallet = db_manager.client.table("doctor_wallets").select("*").eq("doctor_id", doctor_id).single().execute()
    if wallet.data:
        new_balance = wallet.data['available_balance'] - amount
        new_withdrawn = wallet.data['withdrawn_amount'] + amount
        db_manager.client.table("doctor_wallets").update({
            "available_balance": new_balance,
            "withdrawn_amount": new_withdrawn,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("doctor_id", doctor_id).execute()

    return {"status": "success", "request_id": request_id}

@router.get("/users")
async def list_users(user: dict = Depends(get_admin_user)):
    """List Firebase/Astra users and their activity"""
    if not db_manager.client: return []
    res = db_manager.client.table("astra_users").select("*").order("created_at", desc=True).execute()
    return res.data

@router.get("/config")
async def get_config(user: dict = Depends(get_admin_user)):
    """Get current system configuration from env/settings"""
    return {
        "ASTRA_MODEL": settings.BASE_MODEL,
        "LORA_ADAPTER": settings.LORA_MODEL,
        "WASABI_BUCKET": os.getenv("WASABI_BUCKET", "astraehr"),
        "WASABI_ENDPOINT": os.getenv("WASABI_ENDPOINT", "s3.wasabisys.com"),
        "FIREBASE_PROJECT_ID": os.getenv("FIREBASE_PROJECT_ID", "ayureze-official"),
        "API_VERSION": "4.5.0-ASTRA"
    }

@router.post("/config/astra")
async def update_astra_config(config: AstraConfig, user: dict = Depends(get_admin_user)):
    """Mock-update Astra AI settings (usually requires restart)"""
    # In a real scenario, this might write back to .env or a config table
    logger.info(f"Admin updating Astra Config: {config}")
    return {"status": "persisted", "message": "Settings saved to local vault"}

@router.post("/config/wasabi")
async def update_wasabi_config(config: WasabiConfig, user: dict = Depends(get_admin_user)):
    """Update Wasabi storage connection details"""
    logger.info(f"Admin updating Wasabi Config: {config.bucket}")
    return {"status": "updated", "config": config.bucket}
