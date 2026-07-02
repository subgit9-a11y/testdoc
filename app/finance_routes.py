from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.finance_service import finance_service

finance_router = APIRouter()

class WithdrawRequest(BaseModel):
    amount: int

class BankDetailsRequest(BaseModel):
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    account_holder_name: str
    upi_id: Optional[str] = None

@finance_router.get("/wallet/{doctor_id}")
async def get_wallet(doctor_id: str):
    """Get doctor's wallet balance and transactions"""
    summary = await finance_service.get_wallet_summary(doctor_id)
    if "error" in summary:
        raise HTTPException(status_code=500, detail=summary["error"])
    return {"success": True, "data": summary}

@finance_router.post("/wallet/{doctor_id}/bank-details")
async def update_bank_details(doctor_id: str, request: BankDetailsRequest):
    """Save doctor bank details for Cashfree payouts"""
    from app.database import db_manager
    if not db_manager.is_connected():
        raise HTTPException(status_code=500, detail="Database disconnected")
        
    try:
        # Check if wallet exists
        res = db_manager.client.table("doctor_wallets").select("*").eq("doctor_id", doctor_id).execute()
        if not res.data:
            db_manager.client.table("doctor_wallets").insert({
                "doctor_id": doctor_id,
                "bank_account_number": request.bank_account_number,
                "bank_ifsc": request.bank_ifsc,
                "account_holder_name": request.account_holder_name,
                "upi_id": request.upi_id
            }).execute()
        else:
            db_manager.client.table("doctor_wallets").update({
                "bank_account_number": request.bank_account_number,
                "bank_ifsc": request.bank_ifsc,
                "account_holder_name": request.account_holder_name,
                "upi_id": request.upi_id
            }).eq("doctor_id", doctor_id).execute()
            
        return {"success": True, "message": "Payment details saved securely."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@finance_router.post("/wallet/{doctor_id}/withdraw")
async def request_payout(doctor_id: str, request: WithdrawRequest):
    """Initiate a cashfree payout"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
        
    res = await finance_service.request_withdrawal(doctor_id, request.amount)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to process withdrawal"))
        
    return res
