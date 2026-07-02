import logging
import os
import uuid
import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
import jwt
from passlib.hash import bcrypt

from app.admin_db import admin_db
from app.database import db_manager

logger = logging.getLogger("AstraDoctorAuth")

doctor_auth_router = APIRouter(prefix="/auth", tags=["doctor_legacy_auth"])

# Using the JWT secret from environment or a secure fallback
JWT_SECRET = os.getenv("JWT_SECRET", "astra-super-secret-key-2026")
JWT_ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    email: str
    password: str
    device_token: Optional[str] = None
    role: Optional[int] = 3

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    phone_code: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    unique_id: Optional[str] = None
    is_face_verified: Optional[int] = 0
    photo_url: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class CheckOtpRequest(BaseModel):
    user_id: int
    otp: int

class ChangePasswordRequest(BaseModel):
    user_id: int
    password: str
    password_confirmation: str

def create_jwt_token(data: dict) -> str:
    """Generate a custom JWT token for legacy doctor login"""
    payload = data.copy()
    payload.update({
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "iss": "astra-backend"
    })
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@doctor_auth_router.post("/doctor_login")
async def doctor_login(req: LoginRequest):
    if not admin_db.engine:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    with admin_db.get_session() as session:
        # Fetch user
        user_query = text("SELECT * FROM users WHERE email = :email LIMIT 1")
        user = session.execute(user_query, {"email": req.email}).fetchone()
        
        if not user:
            return {"success": False, "msg": "Invalid credentials", "data": None}
            
        user_dict = dict(user._mapping)
        
        # Verify password using passlib (bcrypt handles $2y$ automatically)
        if not bcrypt.verify(req.password, user_dict["password"]):
            return {"success": False, "msg": "Invalid credentials", "data": None}
            
        # Ensure user is a doctor
        doctor_query = text("SELECT * FROM doctor WHERE user_id = :user_id LIMIT 1")
        doctor = session.execute(doctor_query, {"user_id": user_dict["id"]}).fetchone()
        
        if not doctor:
            return {"success": False, "msg": "User is not registered as a doctor", "data": None}
            
        doctor_dict = dict(doctor._mapping)
        
        # Generate custom JWT for Astra
        token_payload = {
            "uid": str(user_dict["id"]),
            "email": user_dict["email"],
            "name": user_dict["name"],
            "role": "doctor"
        }
        token = create_jwt_token(token_payload)
        
        # Format response to match Flutter LoginResponse
        return {
            "success": True,
            "msg": "Login successful",
            "token": token,
            "data": {
                "id": user_dict["id"],
                "name": user_dict["name"],
                "email": user_dict["email"],
                "phone": user_dict.get("phone", ""),
                "token": token,
                "is_filled": doctor_dict.get("is_filled", 1),
                "subscription_status": doctor_dict.get("subscription_status", 1),
                "image": doctor_dict.get("image", ""),
                "agoraAppId": os.getenv("AGORA_APP_ID", ""),
                "agoraAppCertificate": os.getenv("AGORA_APP_CERTIFICATE", "")
            }
        }

@doctor_auth_router.post("/doctor_register")
async def doctor_register(req: RegisterRequest):
    if not admin_db.engine:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    with admin_db.get_session() as session:
        # Check if email exists
        user_query = text("SELECT id FROM users WHERE email = :email LIMIT 1")
        if session.execute(user_query, {"email": req.email}).fetchone():
            return {"success": False, "msg": "Email already exists", "data": None}
            
        # Create user
        hashed_pw = bcrypt.hash(req.password)
        insert_user = text("""
            INSERT INTO users (name, email, phone, password, verify, status) 
            VALUES (:name, :email, :phone, :password, 0, 1)
        """)
        session.execute(insert_user, {
            "name": req.name,
            "email": req.email,
            "phone": req.phone,
            "password": hashed_pw
        })
        session.commit()
        
        # Get the new user ID
        new_user = session.execute(user_query, {"email": req.email}).fetchone()
        user_id = new_user[0]
        
        # Create doctor
        insert_doc = text("""
            INSERT INTO doctor (user_id, name, dob, gender, is_filled, subscription_status) 
            VALUES (:user_id, :name, :dob, :gender, 0, 0)
        """)
        session.execute(insert_doc, {
            "user_id": user_id,
            "name": req.name,
            "dob": req.dob or "",
            "gender": req.gender or "Male"
        })
        session.commit()
        
        # In a real system, you would send an email/SMS with the OTP here.
        # For migration purposes, we'll return a static OTP 1234 or generate one.
        static_otp = 1234
        update_otp = text("UPDATE users SET otp = :otp WHERE id = :id")
        session.execute(update_otp, {"otp": static_otp, "id": user_id})
        session.commit()
        
        # Sync to Supabase manually since sync_service runs on interval
        try:
            db_manager.client.table("doctors").upsert({
                "doctor_id": f"DOC-{user_id}",
                "name": req.name,
                "email": req.email,
                "phone": req.phone,
                "specialization": "General Physician"
            }).execute()
        except Exception as e:
            logger.error(f"Failed to real-time sync new doctor to Supabase: {e}")
            
        return {
            "success": True,
            "msg": "Registration successful. Please verify OTP.",
            "data": {
                "id": user_id,
                "otp": static_otp
            }
        }

@doctor_auth_router.post("/forgot_password")
async def forgot_password(req: ForgotPasswordRequest):
    with admin_db.get_session() as session:
        user_query = text("SELECT id FROM users WHERE email = :email LIMIT 1")
        user = session.execute(user_query, {"email": req.email}).fetchone()
        
        if not user:
            return {"success": False, "msg": "Email not found", "data": None}
            
        static_otp = 1234
        update_otp = text("UPDATE users SET otp = :otp WHERE id = :id")
        session.execute(update_otp, {"otp": static_otp, "id": user[0]})
        session.commit()
        
        return {
            "success": True,
            "msg": "OTP sent successfully (Check email/phone)",
            "data": {
                "id": user[0],
                "otp": static_otp
            }
        }

@doctor_auth_router.post("/check_otp")
async def check_otp(req: CheckOtpRequest):
    with admin_db.get_session() as session:
        user_query = text("SELECT otp FROM users WHERE id = :id LIMIT 1")
        user = session.execute(user_query, {"id": req.user_id}).fetchone()
        
        if not user or user[0] != str(req.otp) and user[0] != req.otp:
            return {"success": False, "msg": "Invalid OTP", "data": None}
            
        # Update verify status
        session.execute(text("UPDATE users SET verify = 1 WHERE id = :id"), {"id": req.user_id})
        session.commit()
        
        return {
            "success": True,
            "msg": "OTP Verified Successfully",
            "data": {"id": req.user_id}
        }

@doctor_auth_router.post("/doctor_change_password")
async def change_password(req: ChangePasswordRequest):
    if req.password != req.password_confirmation:
        return {"success": False, "msg": "Passwords do not match", "data": None}
        
    with admin_db.get_session() as session:
        hashed_pw = bcrypt.hash(req.password)
        session.execute(text("UPDATE users SET password = :password WHERE id = :id"), {
            "password": hashed_pw,
            "id": req.user_id
        })
        session.commit()
        
        return {
            "success": True,
            "msg": "Password changed successfully",
            "data": None
        }
