from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies import get_current_user
from app.services import career_service

router = APIRouter()


@router.get("/career-insights")
async def career_insights(resume_id: str = Query(...), user=Depends(get_current_user)):
    try:
        recommendations = career_service.get_role_recommendations(user_id=user["id"], resume_id=resume_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"recommended_roles": recommendations}


@router.get("/skill-gap")
async def skill_gap(resume_id: str = Query(...), job_id: str = Query(...), user=Depends(get_current_user)):
    try:
        result = career_service.get_skill_gap(user_id=user["id"], resume_id=resume_id, job_id=job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.get("/history")
async def get_history(user=Depends(get_current_user)):
    """
    Returns the user's past analyses. Backed by the `analysis_history` table
    in supabase/schema.sql — wire up a real query here once Supabase is
    connected (see app/services/db_client.py for the connection pattern).
    """
    return {"history": [], "note": "Connect to analysis_history table via db_client for real data."}
