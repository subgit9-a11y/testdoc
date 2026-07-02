import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

# =========================================================
# Shopify Configuration (Required by ShopifyClient)
# =========================================================
try:
    from .shopify_models import PrescriptionRequest, ShopifyDraftOrderResponse
    from .enhanced_product_mapper import enhanced_product_mapper
except ImportError:
    # Handle direct execution for testing if needed
    PrescriptionRequest = Any
    ShopifyDraftOrderResponse = Any
    enhanced_product_mapper = None

logger = logging.getLogger(__name__)

# =========================================================
# Shopify Exception Classes (REQUIRED by other modules)
# =========================================================

class ShopifyAPIError(Exception):
    """Base Shopify API error"""
    def __init__(self, message: str, status_code: Optional[int] = None, shopify_errors: Optional[Dict] = None):
        super().__init__(message)
        self.user_friendly_message = "A Shopify API error occurred. Please try again."
        self.status_code = status_code
        self.shopify_errors = shopify_errors or {}

class ShopifyValidationError(ShopifyAPIError):
    """Invalid request or data sent to Shopify"""
    def __init__(self, message: str, field_errors: Optional[List[Dict]] = None, error_code: str = "validation_error"):
        super().__init__(message, status_code=422)
        self.user_friendly_message = message
        self.field_errors = field_errors or []
        self.error_code = error_code

class ShopifyRateLimitError(ShopifyAPIError):
    """Shopify rate limit exceeded"""
    def __init__(self, message: str, retry_after: int = 60, calls_remaining: int = 0):
        super().__init__(message, status_code=429)
        self.user_friendly_message = f"Rate limit exceeded. Please retry after {retry_after} seconds."
        self.retry_after = retry_after
        self.calls_remaining = calls_remaining


# =========================================================
# Shopify Client
# =========================================================

class ShopifyClient:
    """
    Central Shopify integration client
    Used by:
    - Smart Auto Cart
    - Prescription Automation
    - Shopify Auto Sync
    """

    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_SHOP_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_key = os.getenv("SHOPIFY_API_KEY")
        self.api_secret = os.getenv("SHOPIFY_API_SECRET")
        
        # 🔐 REQUIRED ATTRIBUTE (many modules expect this)
        self.mock_mode: bool = False
        self.auth = None
        self.headers = {}

        if not self.shop_url or not (self.access_token or (self.api_key and self.api_secret)):
            logger.warning("Shopify credentials not found. Running in mock mode.")
            self.mock_mode = True
            self.base_url = None
            return

        # Normalize shop URL to prevent double https:// or missing .myshopify.com
        if self.shop_url:
            if not self.shop_url.startswith("https://"):
                self.shop_url = f"https://{self.shop_url}"
            if not self.shop_url.endswith(".myshopify.com") and not ".myshopify.com/" in self.shop_url:
                self.shop_url = f"{self.shop_url.rstrip('/')}.myshopify.com"
        
        # Extract domain for base URL
        shop_domain = self.shop_url.replace("https://", "").rstrip("/")
        self.base_url = f"https://{shop_domain}/admin/api/2024-01"
        
        if self.access_token:
            self.headers = {
                "X-Shopify-Access-Token": self.access_token,
                "Content-Type": "application/json",
            }
        elif self.api_key and self.api_secret:
            self.auth = (self.api_key, self.api_secret)
            self.headers = {
                "Content-Type": "application/json",
            }

        logger.info("Shopify client initialized")

    # =====================================================
    # Internal request helper
    # =====================================================

    def _request(self, method: str, endpoint: str, payload: Optional[dict] = None):
        if self.mock_mode:
            raise ShopifyAPIError("Shopify is running in mock mode")

        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=self.headers,
            auth=self.auth,
            timeout=30
        )

        if response.status_code == 429:
            raise ShopifyRateLimitError("Shopify rate limit exceeded")

        if response.status_code >= 400:
            raise ShopifyAPIError(response.text)

        return response.json()

    # =====================================================
    # Product Search (used by /shopify/products/search)
    # =====================================================

    def search_product(self, query: str) -> Dict:
        if self.mock_mode:
            return {
                "medicine_name": query,
                "is_available": False,
                "mock_mode": True
            }

        data = self._request("GET", f"/products.json?limit=250")

        for product in data.get("products", []):
            title = product.get("title", "")
            if query.lower() in title.lower():
                variants = product.get("variants", [])
                if variants:
                    return {
                        "medicine_name": query,
                        "shopify_variant_id": variants[0]["id"],
                        "shopify_product_title": title,
                        "is_available": True,
                        "suggested_alternatives": []
                    }

        return {
            "medicine_name": query,
            "is_available": False,
            "suggested_alternatives": []
        }

    # =====================================================
    # Draft Order Creation (CORE FEATURE)
    # =====================================================

    def create_draft_order(self, prescription: Any) -> Any:
        """
        Create Shopify draft order from PrescriptionRequest
        
        Args:
            prescription: PrescriptionRequest pydantic model
            
        Returns:
            ShopifyDraftOrderResponse-compatible dictionary
        """
        if self.mock_mode:
            logger.info(f"Mock mode: Simulated draft order for {prescription.patient.name}")
            return ShopifyDraftOrderResponse(
                draft_order_id="999999999",
                invoice_url=f"https://{self.shop_url}/999999999/authenticate?key=mock" if self.shop_url else "https://mock-store.myshopify.com/999999999/authenticate",
                status="open",
                total_price="1500.00",
                line_items_count=len(prescription.prescriptions),
                unmapped_medicines=[]
            )

        line_items = []
        unmapped_medicines = []

        for item in prescription.prescriptions:
            # Use EnhancedProductMapper for cached fuzzy lookups
            product_info = enhanced_product_mapper.get_product_info(item.medicine) if enhanced_product_mapper else {}
            
            if product_info.get("is_available") and product_info.get("shopify_variant_id"):
                # Ensure variant_id is numeric (extract from GID if necessary)
                v_id = str(product_info["shopify_variant_id"])
                if "/" in v_id:
                    v_id = v_id.split("/")[-1]
                
                line_items.append({
                    "variant_id": int(v_id) if v_id.isdigit() else v_id,
                    "quantity": item.quantity,
                    "properties": [
                        {"name": "Dose", "value": item.dose},
                        {"name": "Schedule", "value": item.schedule},
                        {"name": "Timing", "value": item.timing},
                        {"name": "Duration", "value": item.duration or "As directed"},
                        {"name": "Instructions", "value": item.instructions or "None"}
                    ]
                })
            else:
                unmapped_medicines.append(item.medicine)

        if not line_items:
            raise ShopifyValidationError(
                "No medicines from this prescription were found in our Shopify store. "
                "Please add products manually or check medicine names.",
                error_code="no_items_found"
            )

        # Build Shopify payload
        doctor_name = prescription.doctor.name if prescription.doctor else "Ayureze Team"
        patient_note = (
            f"Ayureze Prescription - {prescription.diagnosis} | "
            f"Patient: {prescription.patient.name}, Age: {prescription.patient.age} | "
            f"Doctor: {doctor_name}"
        )

        # Better name splitting
        full_name = (prescription.patient.name or "Unknown Patient").strip()
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        customer_data = {
            "first_name": first_name,
            "last_name": last_name,
        }
        
        # Only include non-empty fields (Shopify rejects empty strings for email/phone)
        if prescription.patient.email:
            customer_data["email"] = prescription.patient.email
        if prescription.patient.contact:
            # Contact can be phone or email in this system, but Shopify phone must be valid
            if "@" not in prescription.patient.contact:
                 customer_data["phone"] = prescription.patient.contact

        # Build tags
        tags_list = ["ayureze_astra"]
        if hasattr(prescription, 'prescription_id') and prescription.prescription_id:
            tags_list.append(f"prescription:{prescription.prescription_id}")

        payload = {
            "draft_order": {
                "line_items": line_items,
                "note": f"{patient_note} | ID: {getattr(prescription, 'prescription_id', 'N/A')}",
                "customer": customer_data,
                "use_customer_default_address": True,
                "tags": ", ".join(tags_list)
            }
        }

        try:
            result = self._request("POST", "/draft_orders.json", payload)
            draft_order = result.get("draft_order", {})
            
            # Return response compatible with ShopifyDraftOrderResponse
            return ShopifyDraftOrderResponse(
                draft_order_id=str(draft_order.get("id")),
                invoice_url=draft_order.get("invoice_url", ""),
                status=draft_order.get("status", "open"),
                total_price=draft_order.get("total_price", "0.00"),
                line_items_count=len(draft_order.get("line_items", [])),
                unmapped_medicines=unmapped_medicines
            )
        except Exception as e:
            logger.error(f"Failed to create draft order: {e}")
            if isinstance(e, ShopifyAPIError):
                raise
            raise ShopifyAPIError(f"Failed to create Shopify draft order: {str(e)}")

    def complete_draft_order(self, draft_order_id: str, payment_pending: bool = True) -> Dict:
        """
        Complete a draft order and turn it into a real order.
        
        Args:
            draft_order_id: ID of the draft order to complete
            payment_pending: If True, the resulting order will have financial_status='pending' (perfect for COD)
            
        Returns:
            The created Order object
        """
        if self.mock_mode:
            logger.info(f"Mock mode: Simulated completion of draft order {draft_order_id}")
            return {"id": "888888888", "status": "pending", "total_price": "1500.00"}

        endpoint = f"/draft_orders/{draft_order_id}/complete.json"
        if payment_pending:
            endpoint += "?payment_pending=true"

        try:
            result = self._request("PUT", endpoint)
            return result.get("draft_order") or result.get("order")
        except Exception as e:
            logger.error(f"Failed to complete draft order {draft_order_id}: {e}")
            raise ShopifyAPIError(f"Failed to complete draft order: {str(e)}")

    def get_draft_order(self, draft_order_id: int) -> Optional[Dict]:
        """Fetch draft order details from Shopify"""
        if self.mock_mode:
            return {
                "id": draft_order_id,
                "status": "open",
                "total_price": "1500.00",
                "line_items": [],
                "note": "Mock draft order note"
            }

        try:
            result = self._request("GET", f"/draft_orders/{draft_order_id}.json")
            return result.get("draft_order")
        except Exception as e:
            logger.error(f"Error fetching draft order {draft_order_id}: {e}")
            return None

    def validate_prescription(self, prescription: Any) -> List[Dict]:
        """
        Perform pre-flight validation on a prescription
        Returns list of validation error dictionaries
        """
        errors = []
        
        if not prescription.prescriptions:
            errors.append({"field": "prescriptions", "error": "Prescription must contain at least one medicine"})
            
        for i, item in enumerate(prescription.prescriptions):
            if not item.medicine:
                errors.append({
                    "field": f"prescriptions[{i}].medicine", 
                    "error": "Medicine name is required",
                    "prescription_index": i
                })
            if item.quantity < 1:
                errors.append({
                    "field": f"prescriptions[{i}].quantity", 
                    "error": "Quantity must be at least 1",
                    "prescription_index": i
                })
                
        return errors

    def create_order(self, prescription: Any, payment_pending: bool = True) -> Any:
        """
        Directly create a real Draft Order and complete it as a real Order (COD).
        
        Args:
            prescription: PrescriptionRequest
            payment_pending: If True, marks financial_status as 'pending' (COD style)
            
        Returns:
            The created Order ID
        """
        # 1. Create the draft order
        draft_response = self.create_draft_order(prescription)
        d_id = draft_response.draft_order_id
        
        # 2. Complete the draft order
        order_info = self.complete_draft_order(d_id, payment_pending=payment_pending)
        
        return {
            "order_id": order_info.get("id") or order_info.get("order_id"),
            "name": order_info.get("name"),
            "status": "pending_cod" if payment_pending else "paid",
            "invoice_url": draft_response.invoice_url
        }


# =========================================================
# Singleton instance (USED EVERYWHERE)
# =========================================================

# =========================================================
# Singleton instance (USED EVERYWHERE)
# =========================================================

# Helper to create client without causing infinite recursion if models fail
def create_initial_client():
    try:
        return ShopifyClient()
    except Exception as e:
        logger.error(f"Failed to initialize ShopifyClient: {e}")
        # Create a basic client and force mock mode
        client = ShopifyClient.__new__(ShopifyClient)
        client.mock_mode = True
        client.shop_url = "mock-store.myshopify.com"
        client.access_token = "mock-token"
        client.base_url = None
        client.headers = {}
        return client

shopify_client = create_initial_client()

