"""
Supabase connection helper for Astra
Points to the central db_manager for consistency.
"""

import logging
from app.database import db_manager

logger = logging.getLogger(__name__)

def get_supabase_client():
    """Get the central Supabase client from db_manager"""
    if not db_manager.is_connected():
        logger.warning("Supabase db_manager not connected")
        return None
    return db_manager.client
