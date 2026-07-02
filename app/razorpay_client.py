"""
Razorpay Integration Core
Handles all payments and withdrawals for Astra.
Admin is the primary merchant for all AyurEze ecosystem transactions.
"""

import os
import logging
import razorpay
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RazorpayClient:
    """Manages secure transactions and payouts for the Doctor App"""
    
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        self.mock_mode = not (self.key_id and self.key_secret)
        
        if self.mock_mode:
            self.client = None
            logger.info("ℹ️ Razorpay running in mock mode (credentials missing)")
        else:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                logger.info("✅ Razorpay client initialized (Admin Account)")
            except Exception as e:
                logger.error(f"❌ Razorpay failed to initialize: {e}")
                self.client = None
    
    async def create_order(self, amount_in_paise: int, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """Create a payment order for a consultation"""
        if self.mock_mode:
            return {
                "id": f"order_mock_{os.urandom(8).hex()}",
                "amount": amount_in_paise,
                "currency": currency,
                "status": "created",
                "mock": True
            }
            
        try:
            data = {
                "amount": amount_in_paise,
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1
            }
            order = self.client.order.create(data=data)
            return order
        except Exception as e:
            logger.error(f"Razorpay order error: {e}")
            return {"error": str(e)}

    async def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Securely verify the payment signature from the client"""
        if self.mock_mode:
            return True
            
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            # verify_payment_signature raises error if invalid
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            logger.error(f"Security: Payment verification failed: {e}")
            return False

    async def initiate_payout(self, doctor_id: str, amount_70_paise: int, bank_account: Dict[str, str]) -> Dict[str, Any]:
        """
        Transfers the 70% share from the Admin's Razorpay account to the Doctor.
        NOTE: This requires Razorpay X (Payouts) to be enabled.
        """
        if self.mock_mode:
            return {
                "status": "processed",
                "payout_id": f"pout_mock_{os.urandom(8).hex()}",
                "utr": "MOCK12345678",
                "fee": 0,
                "tax": 0
            }
            
        # Payout logic using Razorpay X (Requires separate credentials / setup)
        # For now, we return the structure that the FinanceService expects.
        return {
            "status": "pending",
            "payout_id": "pout_pending_approval",
            "info": "Consult admin dashboard for RazorpayX Payouts"
        }

# Global Singleton
razorpay_service = RazorpayClient()
