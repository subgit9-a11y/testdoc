"""
Patient Auto-Cart Integration Router (Supabase Powered)
Allows the Patient App to retrieve the latest prescribed medicines and a direct checkout link via Supabase.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/patients/active-cart", tags=["Patient App Integration"])

class CartItem(BaseModel):
    medicine_name: str
    quantity: int
    price: Optional[str] = None
    is_available: bool = True

class ActiveCartResponse(BaseModel):
    has_active_cart: bool
    prescription_id: Optional[str] = None
    diagnosis: Optional[str] = None
    total_amount: Optional[str] = None
    invoice_url: Optional[str] = None
    items: List[CartItem] = []
    message: Optional[str] = None

@router.get("/{patient_id}", response_model=ActiveCartResponse)
async def get_active_prescription_cart(
    patient_id: str
):
    """
    Retrieve the latest unpaid prescription from Supabase for a patient.
    Provides the Shopify invoice URL for one-click checkout in the patient app.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
        
    try:
        # 1. Verify patient exists
        patient = await db_manager.get_patient_profile(patient_id)
        if not patient:
            # Try by code
            res = db_manager.client.table("patient_profiles").select("*").eq("patient_code", patient_id).execute() if db_manager.client else None
            if res and res.data:
                patient = res.data[0]
            else:
                raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_id = patient.get("patient_id")

        # 2. Get latest PrescriptionRecord from Supabase that is unpaid
        if not db_manager.client: return ActiveCartResponse(has_active_cart=False)
        
        res_rx = db_manager.client.table("prescription_records").select("*").eq("patient_id", patient_id).eq("payment_status", "pending").order("prescribed_at", desc=True).limit(1).execute()
        
        if not res_rx.data:
            return ActiveCartResponse(
                has_active_cart=False, 
                message="No pending prescription cart found."
            )
            
        prescription = res_rx.data[0]
        rx_id = prescription.get("prescription_id")
        
        # 3. Get line items
        res_meds = db_manager.client.table("prescribed_medicines").select("*").eq("prescription_id", rx_id).execute()
        items = res_meds.data or []
        
        return ActiveCartResponse(
            has_active_cart=True,
            prescription_id=rx_id,
            diagnosis=prescription.get("diagnosis"),
            total_amount=prescription.get("total_amount"),
            invoice_url=prescription.get("invoice_url"),
            items=[CartItem(
                medicine_name=i.get("medicine_name"),
                quantity=i.get("quantity", 1),
                price=i.get("unit_price"),
                is_available=i.get("is_available", True)
            ) for i in items]
        )

    except HTTPException:
        raise
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error fetching active cart: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching cart link")
