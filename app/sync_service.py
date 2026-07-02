import logging
import httpx
from datetime import datetime, timezone
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SyncService:
    """
    Bridge service to sync Supabase Astra backend data 
    back to the legacy Laravel MySQL database (ayureze.org).
    """
    def __init__(self):
        self.laravel_api_url = os.getenv("LARAVEL_API_URL", "https://ayureze.org/public/api")
        self.laravel_api_key = os.getenv("LARAVEL_API_KEY", "secret-key-placeholder")
        
    async def sync_doctor(self, doctor_data: Dict[str, Any]) -> bool:
        """Syncs a doctor created on Astra to the Laravel MySQL DB"""
        try:
            # We would make an HTTP POST to Laravel's internal sync endpoint
            url = f"{self.laravel_api_url}/internal/sync/doctor"
            headers = {"Authorization": f"Bearer {self.laravel_api_key}"}
            
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=doctor_data, headers=headers)
                
            if res.status_code in [200, 201]:
                logger.info(f"Successfully synced Dr {doctor_data.get('id')} to Laravel DB")
                return True
                
            logger.error(f"Failed to sync Dr {doctor_data.get('id')} to Laravel DB: {res.text}")
            return False
        except Exception as e:
            logger.error(f"Sync Doctor Error: {e}")
            return False

    async def sync_booking(self, booking_data: Dict[str, Any]) -> bool:
        """Syncs a consultation booking to Laravel"""
        try:
            url = f"{self.laravel_api_url}/internal/sync/booking"
            headers = {"Authorization": f"Bearer {self.laravel_api_key}"}
            
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=booking_data, headers=headers)
                
            if res.status_code in [200, 201]:
                logger.info(f"Successfully synced Booking {booking_data.get('consultation_id')} to Laravel DB")
                return True
                
            logger.error(f"Failed to sync Booking {booking_data.get('consultation_id')} to Laravel DB: {res.text}")
            return False
        except Exception as e:
            logger.error(f"Sync Booking Error: {e}")
            return False

sync_service = SyncService()
