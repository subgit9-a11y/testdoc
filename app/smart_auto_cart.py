"""
Smart Auto-Cart Router (Supabase Powered)
Prescription to Shopify Draft Order Pipeline via Supabase.
"""

import logging
import uuid
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone

from .shopify_models import (
    PrescriptionRequest, 
    ShopifyDraftOrderResponse, 
    ProductMappingInfo
)
from .shopify_client import shopify_client, ShopifyValidationError, ShopifyRateLimitError, ShopifyAPIError
from .shopify_api_service import shopify_api
from .firebase_utils import firebase_service
from .patient_tokens import patient_token_service
from .prescription_pdf_service import prescription_pdf_service
from .database import db_manager
from .rate_limiter import rate_limiter, get_client_id
from .audit_logger import audit_logger
from .firebase_auth_middleware import require_doctor_auth

# AI Brain Client for shop assist
from .astra_brain_client import get_brain_client

logger = logging.getLogger(__name__)

# Create router for Smart Auto-Cart endpoints
router = APIRouter(prefix="/shopify", tags=["Smart Auto-Cart"])


# ============================================================================
# AI Shop Assist Models
# ============================================================================

class ShopAssistRequest(BaseModel):
    """Request for AI-powered product recommendations"""
    query: str
    language: str = "en"

class ShopAssistResponse(BaseModel):
    """Response with AI product recommendations"""
    success: bool
    query: str
    suggested_products: List[Dict]
    ai_reasoning: str
    shopify_matches: List[Dict]


# ============================================================================
# AI-Powered Shop Assist Endpoints
# ============================================================================

@router.post("/ai-shop-assist", response_model=ShopAssistResponse)
async def ai_shop_assist(request: ShopAssistRequest):
    """AI-powered shop assistant with symptom to product mapping"""
    try:
        brain = get_brain_client()
        result = await brain.shop_assist(request.query)
        
        suggested_products = []
        ai_reasoning = ""
        
        if result.get("success"):
            try:
                result_data = json.loads(result.get("result", "{}"))
                suggested_product = result_data.get("suggested_product")
                if suggested_product:
                    suggested_products.append({"name": suggested_product, "source": "ai"})
                ai_reasoning = result_data.get("reasoning", "Based on Ayurvedic principles")
            except:
                ai_reasoning = result.get("result", "")
        
        shopify_matches = []
        for product in suggested_products:
            try:
                product_info = shopify_api.get_product_info(product["name"])
                if product_info.get("is_available"):
                    shopify_matches.append(product_info)
            except:
                pass
        
        return ShopAssistResponse(
            success=True,
            query=request.query,
            suggested_products=suggested_products,
            ai_reasoning=ai_reasoning,
            shopify_matches=shopify_matches
        )
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"AI Shop Assist error: {e}")
        return ShopAssistResponse(
            success=False,
            query=request.query,
            suggested_products=[],
            ai_reasoning=f"Error: {str(e)}",
            shopify_matches=[]
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _sanitize_patient_id(name: str) -> str:
    """Safely sanitize patient name to create valid ID"""
    import re
    sanitized = re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_'))
    return sanitized if sanitized else "unknown_patient"


async def _send_prescription_notification(
    prescription: PrescriptionRequest, 
    draft_order_response: ShopifyDraftOrderResponse
):
    """Send push notification and WhatsApp message via Supabase tracking"""
    try:
        patient_id = getattr(prescription.patient, 'patient_id', None) or \
                    getattr(prescription.patient, 'id', None)
        
        if not patient_id and hasattr(prescription.patient, 'name') and prescription.patient.name:
            patient_id = _sanitize_patient_id(prescription.patient.name)
        
        if not patient_id: return
        
        fcm_token = patient_token_service.get_fcm_token(patient_id)
        if fcm_token:
            firebase_service.send_prescription_notification(
                token=fcm_token,
                doctor_name=prescription.doctor.name,
                patient_name=prescription.patient.name,
                invoice_url=draft_order_response.invoice_url,
                draft_order_id=draft_order_response.draft_order_id
            )
        
        patient_phone = getattr(prescription.patient, 'phone', None)
        if patient_phone:
            try:
                from app.medicine_reminders.custom_whatsapp_client import CustomWhatsAppClient
                whatsapp_client = CustomWhatsAppClient()
                medicines_list = [f"- {med.medicine}" for med in prescription.prescriptions]
                await whatsapp_client.send_order_confirmation(
                    customer_phone=patient_phone,
                    customer_name=prescription.patient.name,
                    order_number=draft_order_response.draft_order_id,
                    order_total=str(draft_order_response.total_price),
                    items=medicines_list,
                    tracking_url=draft_order_response.invoice_url
                )
            except: pass
            
    except HTTPException:

            
        raise

            
    except Exception as e:
        logger.error(f"Notification error: {e}")

@router.post("/draft-order", response_model=ShopifyDraftOrderResponse)
async def create_prescription_draft_order(
    prescription: PrescriptionRequest, 
    request: Request,
    doctor: Dict[str, Any] = Depends(require_doctor_auth)
):
    """Create Shopify draft order and save to Supabase (Doctor Only)"""
    client_ip = get_client_id(request)
    allowed, remaining = rate_limiter.is_allowed(client_id=client_ip, max_requests=10, window_seconds=60)
    
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # 1. Patient Lookup in Supabase
        verified_patient_id = prescription.patient.patient_id
        if db_manager.is_connected() and verified_patient_id:
            # Try lookup by code
            res = db_manager.client.table("patient_profiles").select("*").eq("patient_code", verified_patient_id.upper()).execute() if db_manager.client else None
            if res and res.data:
                verified_patient_id = res.data[0].get("patient_id")
        
        # 1.5 Generate Prescription ID if not present
        if not getattr(prescription, 'prescription_id', None):
            prescription.prescription_id = f"rx_{uuid.uuid4().hex[:12]}"
 
        # 2. Create Shopify draft order
        draft_order_response = shopify_client.create_draft_order(prescription)
        
        # IMMUTABLE AUDIT TRAIL LOGGING (Issue #12)
        audit_logger.log_event(
            event_type="shopify_cart_creation",
            actor_id=doctor.get("user_id", "system"),
            action_details="Doctor created a Shopify draft order cart for a patient.",
            payload=prescription.dict(),
            session_id=prescription.prescription_id
        )
        
        # 3. Save to Supabase
        prescription_id = prescription.prescription_id
        if db_manager.is_connected() and db_manager.client:
            try:
                rx_data = {
                    "prescription_id": prescription_id,
                    "patient_id": verified_patient_id or "ext_unverified",
                    "doctor_id": doctor.get("user_id") or (prescription.doctor.regn_no if prescription.doctor else "AY999"),
                    "diagnosis": prescription.diagnosis,
                    "notes": prescription.doctor_notes or "",
                    "draft_order_id": str(draft_order_response.draft_order_id),
                    "invoice_url": draft_order_response.invoice_url,
                    "total_amount": str(draft_order_response.total_price),
                    "status": "created",
                    "prescribed_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Save main record
                db_manager.client.table("prescription_records").insert(rx_data).execute()
                
                # Save medicines
                meds = []
                for med in prescription.prescriptions:
                    meds.append({
                        "prescription_id": rx_id,
                        "medicine_name": med.medicine,
                        "quantity": med.quantity,
                        "dose": med.dose,
                        "schedule": med.schedule,
                        "timing": med.timing,
                        "duration": med.duration or "As directed",
                        "instructions": med.instructions or "None"
                    })
                db_manager.client.table("prescribed_medicines").insert(meds).execute()
                prescription_id = rx_id
            except HTTPException:

                raise

            except Exception as e:
                logger.error(f"Supabase save failed: {e}")
        
        # 4. Success notifications
        await _send_prescription_notification(prescription, draft_order_response)
        
        # 5. Update status
        if prescription_id and db_manager.client:
            db_manager.client.table("prescription_records").update({"status": "notified"}).eq("prescription_id", prescription_id).execute()
        
        draft_order_response.prescription_id = prescription_id
        return draft_order_response
        
    except ShopifyValidationError as e:
        raise HTTPException(status_code=422, detail={"error": e.user_friendly_message})
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
@router.post("/real-order-cod")
async def create_real_order_cod(
    prescription: PrescriptionRequest,
    doctor: Dict[str, Any] = Depends(require_doctor_auth)
):
    """Direct COD order via Shopify and Supabase tracking (Doctor Only)"""
    try:
        draft_response = shopify_client.create_draft_order(prescription)
        order_info = shopify_client.complete_draft_order(draft_response.draft_order_id, payment_pending=True)
        
        return {
            "success": True,
            "order_id": order_info.get("id"),
            "order_name": order_info.get("name"),
            "financial_status": order_info.get("financial_status"),
            "invoice_url": draft_response.invoice_url
        }
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"COD order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy", "database": "supabase" if db_manager.is_connected() else "disconnected"}

@router.post("/validate-prescription")
async def validate_prescription_only(prescription: PrescriptionRequest):
    """
    Validate prescription without creating draft order
    
    Returns validation results and product mapping information
    """
    try:
        # Validate prescription format
        validation_errors = shopify_client.validate_prescription(prescription)
        
        # Check product mappings
        medicine_names = [item.medicine for item in prescription.prescriptions]
        # Get product information for all medicines from Shopify API
        mapping_results = []
        for medicine_name in medicine_names:
            product_info = shopify_api.get_product_info(medicine_name)
            mapping_results.append(product_info)
        
        # Count available vs unavailable medicines
        available_count = sum(1 for result in mapping_results if result["is_available"])
        total_count = len(medicine_names)
        
        return {
            "validation_status": "valid" if not validation_errors else "invalid",
            "validation_errors": validation_errors,
            "product_mapping": mapping_results,
            "summary": {
                "total_medicines": total_count,
                "available_in_shopify": available_count,
                "unavailable_medicines": total_count - available_count,
                "can_create_draft_order": not validation_errors and available_count > 0
            }
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error validating prescription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@router.get("/products/search/{medicine_name}", response_model=ProductMappingInfo)
async def search_medicine_product(medicine_name: str):
    """
    Search for Shopify product mapping by medicine name
    
    Returns product information and alternatives if available
    """
    try:
        product_info = shopify_api.get_product_info(medicine_name)
        
        return ProductMappingInfo(
            medicine_name=product_info["medicine_name"],
            shopify_variant_id=product_info["shopify_variant_id"],
            shopify_product_title=product_info["shopify_product_title"],
            is_available=product_info["is_available"],
            suggested_alternatives=product_info["suggested_alternatives"]
        )
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error searching medicine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/products/available")
async def get_available_medicines():
    """
    Get list of all medicines available in Shopify catalog
    
    Returns complete product catalog for frontend reference
    """
    try:
        medicines = shopify_api.format_medicine_catalog()
        
        price_pending = [m for m in medicines if m.get("price_status") == "price_pending"]
        priced = [m for m in medicines if m.get("price_status") == "available"]
        
        return {
            "total_count": len(medicines),
            "priced_count": len(priced),
            "price_pending_count": len(price_pending),
            "medicines": medicines,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "catalog_version": "1.1"
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error fetching available medicines: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch medicines: {str(e)}"
        )

@router.get("/draft-order/{draft_order_id}")
async def get_draft_order_status(draft_order_id: int):
    """
    Get draft order status and details
    
    Useful for checking order status after creation
    """
    try:
        draft_order = shopify_client.get_draft_order(draft_order_id)
        
        if not draft_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft order {draft_order_id} not found"
            )
        
        return {
            "draft_order_id": draft_order["id"],
            "status": draft_order["status"],
            "invoice_url": draft_order.get("invoice_url"),
            "total_price": draft_order.get("total_price"),
            "line_items_count": len(draft_order.get("line_items", [])),
            "created_at": draft_order.get("created_at"),
            "updated_at": draft_order.get("updated_at")
        }
        
    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error fetching draft order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch draft order: {str(e)}"
        )

@router.get("/health")
async def smart_auto_cart_health():
    """
    Health check for Smart Auto-Cart service
    
    Returns service status and configuration
    """
    try:
        # Check if Shopify is configured
        shopify_configured = not shopify_client.mock_mode
        
        # Check product mapping
        available_medicines_count = len(shopify_api.format_medicine_catalog())
        
        return {
            "service": "Smart Auto-Cart",
            "status": "healthy",
            "shopify_integration": "configured" if shopify_configured else "mock_mode",
            "product_catalog": {
                "available_medicines": available_medicines_count,
                "last_updated": "2024-09-04"
            },
            "features": [
                "Prescription validation",
                "Medicine to Shopify mapping",
                "Draft order creation",
                "Dosage instructions as properties",
                "External therapy notes"
            ]
        }
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"service": "Smart Auto-Cart", "status": "unhealthy", "error": str(e)}
        )

@router.get("/order-details/{draft_order_id}")
async def get_order_details_for_app(draft_order_id: int):
    """
    Get detailed order information for Flutter app display (fixed type mismatch)
    
    Returns prescription details, medicines, patient info, and payment link
    """
    try:
        # Get draft order from Shopify (fixed: now expects int consistently)
        draft_order = shopify_client.get_draft_order(draft_order_id)
        
        if not draft_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {draft_order_id} not found"
            )
        
        # Extract medicines and details from line items
        medicines = []
        total_amount = 0
        
        if 'line_items' in draft_order:
            for item in draft_order['line_items']:
                medicine_info = {
                    "name": item.get('title', 'Unknown Medicine'),
                    "quantity": item.get('quantity', 1),
                    "price": float(item.get('price', 0)),
                    "total_price": float(item.get('price', 0)) * item.get('quantity', 1),
                    "properties": {}
                }
                
                # Extract dosage instructions from properties
                if 'properties' in item:
                    for prop in item['properties']:
                        medicine_info['properties'][prop.get('name', '')] = prop.get('value', '')
                
                medicines.append(medicine_info)
                total_amount += medicine_info['total_price']
        
        # Extract prescription details from order notes
        order_notes = draft_order.get('note', '')
        
        # Parse prescription info from notes
        patient_name = ""
        doctor_name = ""
        diagnosis = ""
        
        # Simple parsing of order notes
        if "Patient:" in order_notes:
            patient_part = order_notes.split("Patient:")[1].split("|")[0].strip()
            if "," in patient_part:
                patient_name = patient_part.split(",")[0].strip()
        
        if "Doctor:" in order_notes:
            doctor_part = order_notes.split("Doctor:")[1].split("(")[0].strip()
            doctor_name = doctor_part
        
        if "PRESCRIPTION -" in order_notes:
            diagnosis = order_notes.split("PRESCRIPTION -")[1].split("|")[0].strip()
        
        # Construct response for Flutter app
        order_details = {
            "order_id": draft_order_id,
            "status": draft_order.get('status', 'open'),
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "diagnosis": diagnosis,
            "medicines": medicines,
            "total_amount": total_amount,
            "currency": "INR",
            "invoice_url": draft_order.get('invoice_url', ''),
            "created_at": draft_order.get('created_at', ''),
            "payment_status": "pending",
            "prescription_notes": order_notes
        }
        
        logger.info(f"Order details retrieved for Flutter app: {draft_order_id}")
        return order_details
        
    except HTTPException:

        
        raise

        
    except Exception as e:
        logger.error(f"Error fetching order details for app {draft_order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order details: {str(e)}"
        )