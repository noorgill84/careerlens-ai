from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import get_current_user, get_current_user_optional
from app.schemas.resume import ResumeAnalysisResponse, EducationOut, ExperienceOut, ProjectOut, SkillOut
from app.services import resume_service

router = APIRouter()


@router.post("/upload", response_model=ResumeAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...), user=Depends(get_current_user_optional)):
    """
    Upload + fully analyze a resume in one call. Works signed-out for the
    demo flow (spec §34) — the analysis is real either way; only persistence
    to the dashboard/history requires being signed in (see `saved` in the response).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    contents = await file.read()
    try:
        analysis = resume_service.process_and_store_resume(
            file_bytes=contents, filename=file.filename, user_id=user["id"] if user else None,
        )
    except resume_service.ResumeProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return _to_response(analysis)


@router.post("/analyze/{resume_id}", response_model=ResumeAnalysisResponse)
async def reanalyze_resume(resume_id: str, user=Depends(get_current_user)):
    """Re-run analysis on an already-uploaded resume (e.g. after taxonomy updates)."""
    analysis = resume_service.reanalyze_resume(resume_id=resume_id, user_id=user["id"])
    if analysis is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return _to_response(analysis)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, user=Depends(get_current_user)):
    """Permanently delete a resume and its analyses (spec §28 — user data ownership)."""
    deleted = resume_service.delete_resume(resume_id=resume_id, user_id=user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found.")


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_resumes(user=Depends(get_current_user)):
    """Delete every resume + cascading analysis this user owns (spec §28 — 'Users must be able to delete' everything)."""
    from app.services import db_client
    count = db_client.delete_all_user_data(user_id=user["id"])
    return {"deleted_count": count}


def _to_response(analysis: resume_service.ResumeAnalysisResult) -> ResumeAnalysisResponse:
    p = analysis.profile
    return ResumeAnalysisResponse(
        resume_id=analysis.resume_id,
        name=p.name, email=p.email, phone=p.phone, linkedin=p.linkedin,
        github=p.github, portfolio=p.portfolio, summary=p.summary,
        education=[EducationOut(institution=e.institution, degree=e.degree,
                                 graduation_year=e.graduation_year, gpa=e.gpa) for e in p.education],
        experience=[ExperienceOut(company=e.company, position=e.position, duration=e.duration) for e in p.experience],
        projects=[ProjectOut(name=pr.name, raw_text=pr.raw_text) for pr in p.projects],
        skills=[SkillOut(canonical=s.canonical, category=s.category, matched=s.matched) for s in analysis.normalized_skills],
        certifications=p.certifications,
        achievements=p.achievements,
        ats_score=analysis.ats_result.overall_score,
        ats_breakdown={
            "formatting": analysis.ats_result.formatting,
            "keyword_optimization": analysis.ats_result.keyword_optimization,
            "skills_coverage": analysis.ats_result.skills_coverage,
            "experience_quality": analysis.ats_result.experience_quality,
            "achievements": analysis.ats_result.achievements,
            "structure": analysis.ats_result.structure,
        },
        ats_disclaimer=analysis.ats_result.disclaimer,
        improvement_suggestions=analysis.improvement_suggestions,
        saved=analysis.saved,
    )
