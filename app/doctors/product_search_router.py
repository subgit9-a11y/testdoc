"""
Product Search Router for Doctors
Allows doctors to search the live Shopify catalog and map medicines during prescription creation.
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.enhanced_product_mapper import enhanced_product_mapper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/doctors/products", tags=["Doctor Product Tools"])

class ProductInfoResponse(BaseModel):
    medicine_name: str
    shopify_variant_id: Optional[str] = None
    shopify_product_title: Optional[str] = None
    price: Optional[str] = None
    is_available: bool = False
    sku: Optional[str] = None
    suggested_alternatives: List[str] = []

@router.get("/search", response_model=List[ProductInfoResponse])
async def search_shopify_products(
    query: str = Query(..., min_length=2, description="Search term for medicine"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for medicines in the Shopify catalog with fuzzy matching.
    Returns details needed for prescription mapping.
    """
    try:
        # Get similar product names
        product_names = enhanced_product_mapper.find_similar_products(query, limit=limit)
        
        results = []
        for name in product_names:
            info = enhanced_product_mapper.get_product_info(name)
            results.append(ProductInfoResponse(**info))
            
        return results
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error searching Shopify products: {e}")
        raise HTTPException(status_code=500, detail="Error searching product catalog")

@router.get("/suggest-from-intake", response_model=List[ProductInfoResponse])
async def suggest_products_from_intake(
    symptoms: str = Query(..., description="Symptoms or primary complaint from AI intake")
):
    """
    Suggest medicines based on extracted symptoms (Mapping AI Intake to Products).
    """
    try:
        # Simple implementation for now: search products using symptom keywords
        # In a more advanced version, we'd use a symptom-to-medicine mapping or LLM
        keywords = symptoms.split(",")
        results = []
        seen_variants = set()
        
        for kw in keywords:
            kw = kw.strip()
            if not kw: continue
            
            names = enhanced_product_mapper.find_similar_products(kw, limit=3)
            for name in names:
                info = enhanced_product_mapper.get_product_info(name)
                if info.get("shopify_variant_id") and info["shopify_variant_id"] not in seen_variants:
                    results.append(ProductInfoResponse(**info))
                    seen_variants.add(info["shopify_variant_id"])
        
        return results[:10]
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error suggesting products from intake: {e}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")

@router.get("/check-availability/{variant_id}")
async def check_medicine_availability(variant_id: str):
    """
    Check real-time availability of a specific medicine variant.
    """
    try:
        # Search in dynamic cache via mapper
        enhanced_product_mapper.load_dynamic_cache()
        
        for cached_name, info in enhanced_product_mapper._dynamic_cache.items():
            if str(info.get("variant_id")) == variant_id:
                return {
                    "variant_id": variant_id,
                    "is_available": info.get("available", False),
                    "price": info.get("price"),
                    "title": info.get("product_title")
                }
        
        return {"variant_id": variant_id, "is_available": False, "message": "Product not found in current session cache"}
    except HTTPException:

        raise

    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=500, detail="Error checking availability")
