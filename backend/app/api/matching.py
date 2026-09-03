from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.schemas.match import MatchRequest, MatchResponse, MatchBreakdownOut
from app.services import matching_service
from app.services.matching_service import ModelUnavailableError

router = APIRouter()


@router.post("/match", response_model=MatchResponse)
async def match_resume_to_job(payload: MatchRequest, user=Depends(get_current_user)):
    try:
        result = matching_service.match_resume_to_job(
            user_id=user["id"], resume_id=payload.resume_id,
            job_id=payload.job_id, job_description=payload.job_description,
        )
    except ModelUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    b = result["breakdown"]
    return MatchResponse(
        breakdown=MatchBreakdownOut(
            overall_score=b.overall_score, semantic_similarity=b.semantic_similarity,
            technical_skills=b.technical_skills, experience=b.experience, education=b.education,
            role_compatibility=b.role_compatibility, resume_quality=b.resume_quality,
            matched_skills=b.matched_skills, missing_skills=b.missing_skills,
        ),
        strengths=result["strengths"], gaps=result["gaps"],
    )
