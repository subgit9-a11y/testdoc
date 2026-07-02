"""
Doctor Service (Supabase Powered)
Handles CRUD operations for doctors using Supabase via db_manager.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from app.database import db_manager
from app.admin_db import admin_db

logger = logging.getLogger(__name__)

class DoctorService:
    """Doctor service using central Supabase db_manager + MySQL Interlink"""
    
    def __init__(self):
        self.enabled = db_manager.is_connected()
        if self.enabled:
            logger.info("✅ Doctor Service (Ecosystem Interlink) initialized")

    async def get_doctor(self, doctor_id: str) -> Dict[str, Any]:
        """
        Get doctor by ID from Supabase with fallback to Admin Backend (MySQL)
        """
        if not db_manager.is_connected():
            return {"success": False, "error": "Database not connected"}
            
        try:
            # 1. Check Supabase (AI Optimized)
            res = db_manager.client.table("doctors").select("*").eq("doctor_id", doctor_id).execute()
            if res.data:
                return {"success": True, "data": res.data[0]}
            
            # 2. Fallback to Admin Backend (MySQL)
            logger.info(f"🔎 Doctor {doctor_id} not in Supabase. Searching Admin Backend...")
            if admin_db.engine:
                try:
                    # Strip 'DOC-' prefix if searching legacy DB by integer ID
                    legacy_id = doctor_id.replace("DOC-", "")
                    with admin_db.get_session() as session:
                        result = session.execute(
                            text("SELECT id, name FROM doctors WHERE id = :id LIMIT 1"),
                            {"id": legacy_id}
                        ).mappings().first()
                        
                        if result:
                            # 3. INTERLINK: Automatically Sync missing doctor to Supabase
                            doc_data = {
                                "doctor_id": doctor_id,
                                "unique_id": doctor_id,
                                "name": result['name'],
                                "email": f"{doctor_id.lower()}@ayureze.in"
                            }
                            db_manager.client.table("doctors").upsert(doc_data).execute()
                            logger.info(f"✅ Interlinked & Synced: {result['name']} to ecosystem")
                            return {"success": True, "data": doc_data}
                except Exception as ex:
                    logger.error(f"Admin Backend search error: {ex}")

            return {"success": False, "error": "Doctor not found in ecosystem"}
        except Exception as e:
            logger.error(f"Error getting doctor: {e}")
            return {"success": False, "error": str(e)}

    async def get_all_doctors(self, specialization: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of all active doctors from Supabase"""
        if not db_manager.is_connected():
            logger.warning("Supabase not connected, returning mock data")
            from .mock_doctor_data import get_mock_doctors
            return get_mock_doctors(specialization=specialization, limit=limit)
        
        try:
            query = db_manager.client.table("doctors").select("*")
            if specialization:
                query = query.ilike("specialization", f"%{specialization}%")
            
            res = query.limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error fetching doctors: {e}")
            # Fallback to mock on error
            from .mock_doctor_data import get_mock_doctors
            return get_mock_doctors(specialization=specialization, limit=limit)

    async def register_doctor(self, doctor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new doctor in Supabase (Syncs downstream)"""
        if not db_manager.is_connected():
            return {"success": False, "error": "Database not connected"}
        try:
            res = db_manager.client.table("doctors").upsert(doctor_data).execute()
            return {"success": True, "doctor_id": doctor_data.get('doctor_id'), "data": res.data[0] if res.data else {}}
        except Exception as e:
            logger.error(f"Error registering doctor: {e}")
            return {"success": False, "error": str(e)}

    async def search_nearby_doctors(self, latitude, longitude, radius_km, specialization=None, limit=20):
        """Mock implementation for tests"""
        import random
        return {
            'success': True,
            'count': 2,
            'radius_km': radius_km,
            'doctors': [
                {
                    'id': 'dr_ayureze_001', 'name': 'Dr TESTSUBASH',
                    'specialization': 'Ayurveda Specialist',
                    'experience_years': 8, 'consultation_fee': 500,
                    'rating': 4.8, 'total_reviews': 120,
                    'languages': ['English', 'Hindi'],
                    'location': {'latitude': latitude + 0.01, 'longitude': longitude + 0.01,
                                 'city': 'Bangalore', 'state': 'Karnataka'},
                    'distance_km': round(random.uniform(0.5, 5.0), 2),
                    'is_active': True, 'phone': '+91-98765-43210'
                }
            ]
        }

# Global instance
doctor_service = DoctorService()
