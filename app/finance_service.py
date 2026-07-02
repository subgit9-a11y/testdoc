"""
Finance Service - Payouts, Commissions, and Wallets
Handles the 30% Admin commission / 70% Doctor share logic.
Backbone for Razorpay integrated withdrawals.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from app.database import db_manager
from app.cashfree_client import cashfree_payouts

logger = logging.getLogger(__name__)

class FinanceService:
    """Manages the medical-fintech core of AyurEze"""
    
    ADMIN_COMMISSION_PERCENT = 30.0
    DOCTOR_SHARE_PERCENT = 70.0

    async def record_consultation_payment(self, doctor_id: str, consultation_id: str, total_fee: int, payment_id: str):
        """
        Processes a successful consultation payment.
        Updates doctor wallet and logs commission.
        """
        if not db_manager.is_connected():
            return False
            
        try:
            # 1. Calculate Split
            admin_cut = int(total_fee * (self.ADMIN_COMMISSION_PERCENT / 100))
            doctor_share = total_fee - admin_cut
            
            # 2. Update Consultation Record
            db_manager.client.table("consultations").update({
                "payment_status": "paid",
                "payment_id": payment_id,
                "total_fee": total_fee
            }).eq("consultation_id", consultation_id).execute()
            
            # 3. Update Doctor Wallet
            # UPSERT ensures wallet exists before update
            wallet_res = db_manager.client.table("doctor_wallets").select("*").eq("doctor_id", doctor_id).execute()
            if not wallet_res.data:
                db_manager.client.table("doctor_wallets").insert({
                    "doctor_id": doctor_id,
                    "total_earned": total_fee,
                    "available_balance": doctor_share,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
                db_manager.client.table("doctor_wallets").update({
                    "balance": current_balance + doctor_share,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("doctor_id", doctor_id).execute()
                
            # 4. Log the Earning Transaction
            db_manager.client.table("wallet_transactions").insert({
                "doctor_id": doctor_id,
                "amount": doctor_share,
                "type": "EARNING",
                "status": "SUCCESS",
                "reference_id": consultation_id,
                "description": f"Consultation fee (70% share)",
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            logger.info(f"💰 Processed payout for {consultation_id}: Dr {doctor_id} (+{doctor_share}) | Admin (+{admin_cut})")
            return True
        except Exception as e:
            logger.error(f"Finance processing error for {consultation_id}: {e}")
            return False

    async def get_wallet_summary(self, doctor_id: str) -> Dict[str, Any]:
        """Fetch real-time earnings (Supabase + Legacy MySQL Interlink)"""
        if not db_manager.is_connected():
            return {"error": "Database disconnected"}
            
        total_earned = 0.0
        available_balance = 0.0
        withdrawn_amount = 0.0
        
        # 1. Fetch from New Supabase Ecosystem
        try:
            res = db_manager.client.table("doctor_wallets").select("*").eq("doctor_id", doctor_id).execute()
            if res.data:
                available_balance += float(res.data[0].get("balance", 0))
                
            # Calculate total earned and withdrawn from transactions
            tx_res = db_manager.client.table("wallet_transactions").select("*").eq("doctor_id", doctor_id).execute()
            if tx_res.data:
                for tx in tx_res.data:
                    if tx["type"] == "EARNING" and tx["status"] == "SUCCESS":
                        total_earned += float(tx["amount"])
                    elif tx["type"] == "WITHDRAWAL" and tx["status"] == "SUCCESS":
                        withdrawn_amount += float(tx["amount"])
                        
        except Exception as e:
            logger.warning(f"Supabase Wallet fetch failed (Table missing?): {e}")
            
        # 2. INTERLINK: Fetch from Legacy MySQL Ecosystem
        try:
            from app.admin_db import admin_db
            from sqlalchemy import text
            
            legacy_id = doctor_id.replace("DOC-", "")
            if admin_db.engine:
                with admin_db.get_session() as session:
                    # Sum all appointment fees for this legacy doctor
                    app_res = session.execute(
                        text("SELECT SUM(amount) as total FROM appointment WHERE doctor_id = :id"),
                        {"id": legacy_id}
                    ).mappings().first()
                    
                    if app_res and app_res['total']:
                        legacy_total = float(app_res['total'])
                        total_earned += legacy_total
                        
                        # Apply Astra's standard 70% doctor share consistency model for legacy earnings
                        legacy_balance = legacy_total * (self.DOCTOR_SHARE_PERCENT / 100)
                        available_balance += legacy_balance
                        
                        logger.info(f"🔄 Wallet Interlink: Added ₹{legacy_total} legacy earnings for {doctor_id}")
        except Exception as e:
            logger.warning(f"Legacy MySQL Wallet Interlink failed: {e}")
            
        return {
            "doctor_id": doctor_id,
            "total_earned": round(total_earned, 2),
            "available_balance": round(available_balance, 2),
            "withdrawn_amount": round(withdrawn_amount, 2)
        }

    async def request_withdrawal(self, doctor_id: str, amount: int) -> Dict[str, Any]:
        """Initiate a withdrawal request of 70% share"""
        if not db_manager.is_connected():
            return {"success": False, "error": "Database disconnected"}
            
        try:
            # Check Balance
            wallet = await self.get_wallet_summary(doctor_id)
            if wallet.get("available_balance", 0) < amount:
                return {"success": False, "error": "Insufficient balance"}
            
            # 2. Add Beneficiary in Cashfree (Idempotent)
            bene_id = f"DOC_{doctor_id}"
            bank_account = wallet_res.data[0].get("bank_account_number")
            ifsc = wallet_res.data[0].get("bank_ifsc")
            upi_id = wallet_res.data[0].get("upi_id")
            name = wallet_res.data[0].get("account_holder_name")
            
            if not name or (not upi_id and (not bank_account or not ifsc)):
                return {"success": False, "error": "Payment details not added. Please update bank or UPI information first."}
                
            bene_added = cashfree_payouts.add_beneficiary(
                bene_id=bene_id, 
                name=name,
                email=f"doc_{doctor_id}@ayureze.in",
                phone="9999999999", # placeholder if not saved
                bank_account=bank_account,
                ifsc=ifsc,
                vpa=upi_id
            )
            
            if not bene_added:
                return {"success": False, "error": "Failed to verify beneficiary with Cashfree."}
                
            # 3. Create Transfer Request
            transfer_id = f"TRF_{uuid.uuid4().hex[:12].upper()}"
            transfer_mode = "upi" if upi_id else "banktransfer"
            cashfree_ref = cashfree_payouts.request_transfer(
                transfer_id=transfer_id,
                bene_id=bene_id,
                amount=amount,
                transfer_mode=transfer_mode,
                remarks=f"Payout for Dr {doctor_id}"
            )
            
            if not cashfree_ref:
                return {"success": False, "error": "Cashfree transfer request failed"}
            
            # 4. Deduct from Wallet (Prevent double spending)
            new_balance = wallet.get("available_balance", 0) - amount
            db_manager.client.table("doctor_wallets").update({
                "balance": new_balance,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("doctor_id", doctor_id).execute()
            
            # 5. Log Transaction
            db_manager.client.table("wallet_transactions").insert({
                "doctor_id": doctor_id,
                "amount": amount,
                "type": "WITHDRAWAL",
                "status": "SUCCESS",
                "reference_id": cashfree_ref,
                "description": f"Cashfree Payout (Ref: {transfer_id})",
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            return {
                "success": True, 
                "message": "Withdrawal processed successfully",
                "reference_id": cashfree_ref,
                "transfer_id": transfer_id
            }
            
        except Exception as e:
            logger.error(f"Withdrawal request failed: {e}")
            return {"success": False, "error": str(e)}

# Global Finance singleton
finance_service = FinanceService()
