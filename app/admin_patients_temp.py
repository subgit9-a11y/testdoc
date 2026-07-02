
@router.get("/patients")
async def get_superadmin_patients():
    """
    Fetches the patient directory and their EHR vault status from Supabase.
    """
    if not db_manager.is_connected():
        raise HTTPException(status_code=503, detail="Supabase not connected")
        
    try:
        # Fetch patients from Supabase
        patients_res = db_manager.client.table("patient_profiles").select("*").execute()
        patients = patients_res.data if patients_res.data else []
        
        # We also want to know how many health cases and EHR documents each has
        for p in patients:
            pid = p.get("patient_id")
            if not pid:
                continue
                
            # Count cases
            cases_res = db_manager.client.table("health_cases").select("count", count="exact").eq("user_id", pid).execute()
            p["total_cases"] = cases_res.count if cases_res.count else 0
            
            # Count EHR documents
            docs_res = db_manager.client.table("documents").select("count", count="exact").eq("patient_id", pid).execute()
            p["total_ehr_docs"] = docs_res.count if docs_res.count else 0
            
            # Get latest case progress if any
            if p["total_cases"] > 0:
                latest_case = db_manager.client.table("health_cases").select("*").eq("user_id", pid).order("created_at", desc=True).limit(1).execute()
                if latest_case.data:
                    p["latest_case_progress"] = latest_case.data[0].get("progress_percentage", 0)
                    p["latest_case_status"] = latest_case.data[0].get("status", "active")
        
        return {
            "success": True,
            "data": patients
        }
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))
