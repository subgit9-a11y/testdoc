
# --- DOCTOR MANAGEMENT ENDPOINTS ---

@router.get("/doctors")
async def get_superadmin_doctors(db: Session = Depends(get_db)):
    """
    Fetches doctors from MySQL and their wallet balances.
    """
    try:
        # Fetch doctors from MySQL
        doctors = []
        try:
            res = db.execute(text("SELECT id, doctor_id, name, email, phone, specialization, is_active, is_verified, consultation_fee FROM doctor_profiles")).mappings().all()
            for doc in res:
                doc_dict = dict(doc)
                # Fetch wallet
                wallet_res = db.execute(text("SELECT total_earned, available_balance, withdrawn_amount FROM doctor_wallets WHERE doctor_id = :did"), {"did": doc_dict["doctor_id"]}).mappings().first()
                if wallet_res:
                    doc_dict.update(dict(wallet_res))
                else:
                    doc_dict.update({"total_earned": 0, "available_balance": 0, "withdrawn_amount": 0})
                doctors.append(doc_dict)
        except Exception as e:
            logger.warning(f"Could not fetch MySQL doctors: {e}")

        return {
            "success": True,
            "data": doctors
        }
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctors/{doctor_id}/toggle-verify")
async def toggle_doctor_verification(doctor_id: str, db: Session = Depends(get_db)):
    """Toggle doctor verification status"""
    try:
        db.execute(
            text("UPDATE doctor_profiles SET is_verified = NOT is_verified WHERE doctor_id = :did"),
            {"did": doctor_id}
        )
        db.commit()
        return {"success": True, "message": "Verification toggled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# --- AI CONTROL CENTER ENDPOINTS ---

@router.get("/ai/journeys")
async def get_superadmin_ai_journeys():
    """
    Fetches all active AI Autopilot journeys from Supabase.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Supabase not connected")
        
    try:
        # Fetch patient care states
        res = db_manager.client.table("patient_care_states").select("*").execute()
        return {
            "success": True,
            "data": res.data if res.data else []
        }
    except Exception as e:
        logger.error(f"Error fetching AI journeys: {e}")
        raise HTTPException(status_code=500, detail=str(e))
