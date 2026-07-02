from fastapi import APIRouter, Depends, HTTPException

from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import db_manager
from app.firebase_auth_middleware import require_firebase_auth

router = APIRouter(prefix="/api/family", tags=["Family Profiles"])

class FamilyMemberCreate(BaseModel):
    name: str
    relation: str
    age: int = None
    gender: str = None
    medical_conditions: str = "[]"
    allergies: str = "[]"

@router.post("/add")
async def add_family_member_api(
    member: FamilyMemberCreate,
    user_token: Dict[str, Any] = Depends(require_firebase_auth)
):
    """Add a family member to the logged-in user's profile using Supabase"""
    try:
        user_id = user_token.get("uid")
        
        member_data = member.dict()
        member_data["primary_patient_id"] = user_id
        
        new_member = await db_manager.add_family_member(member_data)
        
        if not new_member:
            raise HTTPException(status_code=500, detail="Failed to add family member")
            
        return {
            "status": "success", 
            "message": "Family member added", 
            "member_id": new_member.get("member_id")
        }
    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_family_members_api(
    user_token: Dict[str, Any] = Depends(require_firebase_auth)
):
    """List all family members for the logged-in user using Supabase"""
    try:
        user_id = user_token.get("uid")
        members = await db_manager.get_family_members(user_id)
        
        return {
            "status": "success",
            "members": [
                {
                    "member_id": m.get("member_id"),
                    "name": m.get("name"),
                    "relation": m.get("relation"),
                    "age": m.get("age"),
                    "details": f"{m.get('relation')} - {m.get('age')} years" 
                } for m in members
            ]
        }
    except HTTPException:

        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
