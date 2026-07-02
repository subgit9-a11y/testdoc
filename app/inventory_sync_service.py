"""
Inventory Synchronizer - The Bridge to Ayureze Shopify
Periodically pulls product availability, prices, and variant IDs from Shopify
into a local Supabase cache for ultra-fast "In-Stock" prescription checks.
"""

import logging
import asyncio
from datetime import datetime, timezone
from app.database import db_manager
from app.shopify_api_service import shopify_api

logger = logging.getLogger(__name__)

class InventorySyncService:
    """Manages periodic shopify-to-supabase synchronization"""
    
    _is_running = False
    _sync_interval = 3600  # Default 1 hour
    
    async def start_background_sync(self, interval_seconds: int = 3600):
        """Runs the inventory sync task indefinitely in the background"""
        if self._is_running:
            logger.info("InventorySyncService is already working")
            return
            
        self._is_running = True
        self._sync_interval = interval_seconds
        logger.info(f"📦 Inventory Background Sync started (Interval: {interval_seconds}s)")
        
        while self._is_running:
            try:
                # Synchronize
                summary = await self.sync_now()
                logger.info(f"✅ Inventory sync complete: {summary}")
            except Exception as e:
                logger.error(f"❌ Inventory sync failure: {e}")
            
            await asyncio.sleep(self._sync_interval)

    async def sync_now(self):
        """Fetches the latest catalog from Shopify and upserts to Supabase"""
        if not db_manager.is_connected():
            return {"error": "Database disconnected"}
            
        try:
            # 1. Fetch entire catalog from Shopify (optimized via internal cache)
            catalog = shopify_api.format_medicine_catalog()
            
            # 2. Prepare for batch upsert
            inventory_stats = []
            for med in catalog:
                # Map Shopify data to our cache schema
                inventory_stats.append({
                    "medicine_name": med.get("medicine_name"),
                    "shopify_variant_id": med.get("shopify_variant_id"),
                    "is_in_stock": med.get("is_available", True),
                    "price_cents": med.get("price_cents", 0), # Optional calculation
                    "stock_quantity": med.get("stock_quantity", 100), # If Shopify provides it
                    "last_synced_at": datetime.now(timezone.utc).isoformat()
                })
            
            # 3. Batch Upsert to Supabase
            if inventory_stats:
                chunk_size = 50
                for i in range(0, len(inventory_stats), chunk_size):
                    chunk = inventory_stats[i:i + chunk_size]
                    try:
                        db_manager.client.table("medicine_inventory_cache").upsert(
                            chunk, 
                            on_conflict="medicine_name"
                        ).execute()
                    except Exception as inner_e:
                        if 'PGRST205' in str(inner_e) or 'medicine_inventory_cache' in str(inner_e):
                            logger.warning("Supabase table 'medicine_inventory_cache' is missing. Skipping inventory sync until created.")
                            return {"status": "skipped_missing_table"}
                        raise inner_e
                    
            return {"synced_count": len(inventory_stats)}
            
        except Exception as e:
            logger.error(f"Inventory fetch logic error: {e}")
            return {"error": str(e)}

# Global Singleton
inventory_sync_service = InventorySyncService()
