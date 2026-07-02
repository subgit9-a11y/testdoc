"""
Shopify Webhook Handler — Hardened
Receives real-time product/order updates from Shopify webhooks.

Security Hardening (applied):
  1. verify_shopify_webhook now uses hmac.new() correctly and FAILS CLOSED —
     if SHOPIFY_WEBHOOK_SECRET is not configured, ALL webhook calls are rejected
     with 401 to prevent silent fail-open.
  2. /orders/paid now performs full HMAC-SHA256 verification (was completely open).
  3. /draft_orders/completed now performs full HMAC-SHA256 verification (was completely open).
  4. /sync/manual is now protected by require_doctor_auth so it cannot be triggered
     by an unauthenticated user causing a Shopify API storm / DoS.
"""

import logging
import hmac
import hashlib
import os
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from typing import Optional, Dict, Any

from app.firebase_auth_middleware import require_doctor_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/shopify", tags=["Shopify Webhooks"])


# ── HMAC verification ─────────────────────────────────────────────────────────

def verify_shopify_webhook(data: bytes, hmac_header: str, secret: str) -> bool:
    """
    Verify Shopify webhook HMAC-SHA256 signature using constant-time comparison.

    SECURITY NOTE: Uses hmac.compare_digest to prevent timing attacks.
    """
    try:
        computed_hmac = hmac.new(
            secret.encode("utf-8"),
            data,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed_hmac, hmac_header)
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Webhook HMAC verification error: {e}")
        return False


def _require_valid_shopify_signature(body: bytes, hmac_header: Optional[str]) -> None:
    """
    Shared guard: Enforces HMAC validation on every webhook.
    FAILS CLOSED — rejects all requests if SHOPIFY_WEBHOOK_SECRET is not configured,
    preventing a misconfigured environment from silently accepting forged events.
    """
    webhook_secret = os.getenv("SHOPIFY_WEBHOOK_SECRET")

    if not webhook_secret:
        logger.error(
            "SHOPIFY_WEBHOOK_SECRET is not set. Rejecting webhook to prevent "
            "unauthenticated access (fail-closed policy)."
        )
        raise HTTPException(
            status_code=401,
            detail="Webhook endpoint not configured. Contact the server administrator."
        )

    if not hmac_header:
        logger.warning("Webhook received with no HMAC header — rejecting.")
        raise HTTPException(status_code=401, detail="Missing X-Shopify-Hmac-SHA256 header")

    if not verify_shopify_webhook(body, hmac_header, webhook_secret):
        logger.warning("Invalid Shopify webhook HMAC signature — potential spoofed event.")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


# ── Product Webhooks ──────────────────────────────────────────────────────────

@router.post("/products/create")
async def product_created(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    x_shopify_topic: Optional[str] = Header(None)
):
    """Handle product creation webhook from Shopify (HMAC verified)"""
    body = await request.body()
    _require_valid_shopify_signature(body, x_shopify_hmac_sha256)

    data = await request.json()
    logger.info(f"New product created: {data.get('title', 'Unknown')}")

    try:
        from app.shopify_auto_sync import shopify_auto_sync
        await shopify_auto_sync.sync_products()
        return {
            "success": True,
            "message": "Product sync triggered",
            "product_title": data.get("title")
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error syncing after product creation: {e}")
        return {"success": False, "error": str(e)}


@router.post("/products/update")
async def product_updated(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    x_shopify_topic: Optional[str] = Header(None)
):
    """Handle product update webhook from Shopify (HMAC verified)"""
    body = await request.body()
    _require_valid_shopify_signature(body, x_shopify_hmac_sha256)

    data = await request.json()
    logger.info(f"Product updated: {data.get('title', 'Unknown')}")

    try:
        from app.shopify_auto_sync import shopify_auto_sync
        await shopify_auto_sync.sync_products()
        return {
            "success": True,
            "message": "Product sync triggered",
            "product_title": data.get("title")
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error syncing after product update: {e}")
        return {"success": False, "error": str(e)}


@router.post("/products/delete")
async def product_deleted(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    x_shopify_topic: Optional[str] = Header(None)
):
    """Handle product deletion webhook from Shopify (HMAC verified)"""
    body = await request.body()
    _require_valid_shopify_signature(body, x_shopify_hmac_sha256)

    data = await request.json()
    logger.info(f"Product deleted: {data.get('title', 'Unknown')}")

    try:
        from app.shopify_auto_sync import shopify_auto_sync
        await shopify_auto_sync.sync_products()
        return {
            "success": True,
            "message": "Product sync triggered after deletion",
            "product_title": data.get("title")
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error syncing after product deletion: {e}")
        return {"success": False, "error": str(e)}


# ── Order Webhooks (previously unprotected — now HMAC verified) ───────────────

@router.post("/orders/paid")
async def order_paid(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None)
):
    """
    Handle order payment webhook from Shopify.

    SECURITY: Previously had NO HMAC verification. Any attacker could POST to this
    endpoint and forge a payment event, marking a prescription as 'paid' without
    actual money changing hands. Now enforces fail-closed HMAC verification.
    """
    body = await request.body()
    _require_valid_shopify_signature(body, x_shopify_hmac_sha256)

    import json
    try:
        data = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    logger.info(f"Order paid: {data.get('name')}")

    # Find Prescription ID from order tags
    tags = data.get("tags", "")
    prescription_id = None
    if "prescription:" in tags:
        import re
        match = re.search(r"prescription:([a-zA-Z0-9_]+)", tags)
        if match:
            prescription_id = match.group(1)

    if prescription_id:
        try:
            from app.database import db_manager
            if db_manager.is_connected() and db_manager.client:
                db_manager.client.table("prescription_records").update({
                    "status": "paid",
                    "shopify_order_id": str(data.get("id"))
                }).eq("prescription_id", prescription_id).execute()
                logger.info(f"Updated prescription {prescription_id} to PAID")
        except HTTPException:

            raise

        except Exception as e:
            logger.error(f"Failed to update paid status: {e}")

    return {"success": True}


@router.post("/draft_orders/completed")
async def draft_order_completed(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None)
):
    """
    Handle draft order completion (turned into real order).

    SECURITY: Previously had NO HMAC verification. Forged completion events could
    have prematurely marked prescriptions as ordered without an actual transaction.
    Now enforces fail-closed HMAC verification.
    """
    body = await request.body()
    _require_valid_shopify_signature(body, x_shopify_hmac_sha256)

    import json
    try:
        data = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    logger.info(f"Draft order completed: {data.get('id')}")

    tags = data.get("tags", "")
    prescription_id = None
    if "prescription:" in tags:
        import re
        match = re.search(r"prescription:([a-zA-Z0-9_]+)", tags)
        if match:
            prescription_id = match.group(1)

    if prescription_id:
        try:
            from app.database import db_manager
            if db_manager.is_connected() and db_manager.client:
                db_manager.client.table("prescription_records").update({
                    "status": "ordered",
                    "shopify_draft_id": str(data.get("id"))
                }).eq("prescription_id", prescription_id).execute()
        except HTTPException:

            raise

        except Exception as e:
            logger.error(f"Failed to update ordering status: {e}")

    return {"success": True}


# ── Manual Sync (now protected) ───────────────────────────────────────────────

@router.post("/sync/manual")
async def manual_sync(
    doctor: Dict[str, Any] = Depends(require_doctor_auth)
):
    """
    Manually trigger product sync — Doctor Only.

    SECURITY: Previously an unauthenticated GET endpoint that any anonymous user
    could call to hammer the Shopify API repeatedly, causing rate-limit exhaustion
    or a scraping/DoS vector. Now locked behind doctor auth and changed to POST.
    """
    try:
        from app.shopify_auto_sync import shopify_auto_sync
        result = await shopify_auto_sync.sync_products()
        return result
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status")
async def sync_status():
    """Get current sync status (read-only, safe to expose)"""
    try:
        from app.shopify_auto_sync import shopify_auto_sync
        return shopify_auto_sync.get_status()
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
