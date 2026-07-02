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

# --- Dependencies ---

def get_admin_user():
    # TODO: Implement proper admin authentication
    return {"role": "admin"}

# --- Routes ---

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get aggregated system statistics from Supabase"""
    try:
        db_connected = db_manager.is_connected()
        
        # Model status
        try:
            from main_enhanced import model_inference
            model_loaded = model_inference.is_loaded() if model_inference else False
        except:
            model_loaded = False
        
        # Counts from Supabase
        users_count = 0
        doctors_count = 0
        centers_count = 0
        sessions_count = 0

        if db_connected and db_manager.client:
            try:
                # Use head=True for efficient counting in Supabase
                res_u = db_manager.client.table("user_accounts").select("*", count="exact").limit(0).execute()
                users_count = res_u.count or 0
                
                res_d = db_manager.client.table("doctor_profiles").select("*", count="exact").eq("is_active", True).limit(0).execute()
                doctors_count = res_d.count or 0
                
                res_c = db_manager.client.table("treatment_centers").select("*", count="exact").limit(0).execute()
                centers_count = res_c.count or 0
                
                # Active sessions (last 24h)
                yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
                res_s = db_manager.client.table("sessions").select("*", count="exact").gt("updated_at", yesterday).limit(0).execute()
                sessions_count = res_s.count or 0
            except HTTPException:

                raise

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
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config(user: dict = Depends(get_admin_user)):
    """Get current system configuration (safe subset)"""
    return {
        "BASE_MODEL": settings.BASE_MODEL,
        "LORA_MODEL": settings.LORA_MODEL,
        "DEVICE": settings.DEVICE,
        "API_HOST": settings.API_HOST,
        "API_PORT": settings.API_PORT,
        "DEFAULT_TEMPERATURE": settings.DEFAULT_TEMPERATURE
    }

@router.get("/logs")
async def get_logs(lines: int = 100, user: dict = Depends(get_admin_user)):
    """Get recent application logs"""
    log_file = "app.log" 
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                return {"logs": f.readlines()[-lines:]}
        except:
            return {"logs": ["Could not read log file"]}
    return {"logs": ["Log file not found"]}
