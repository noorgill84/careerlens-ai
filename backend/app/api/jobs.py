from fastapi import APIRouter, HTTPException, Query
from app.schemas.job import JobDescriptionIn, JobAnalysisResponse, JobSummary
from app.services import job_service

router = APIRouter()


@router.get("", response_model=list[JobSummary])
async def list_jobs(q: str | None = Query(default=None, description="Natural-language search query")):
    """
    Returns the sample/demo job catalog (spec §14 — clearly labeled, not
    live vacancies). Pass ?q=... for spec §15 semantic-ish search.
    """
    jobs = job_service.search_jobs(q) if q else job_service.list_sample_jobs()
    return [
        JobSummary(
            id=j["id"], title=j["title"], company=j["company"], location=j.get("location"),
            is_sample_data=j["is_sample_data"], required_skills=j["required_skills"],
        )
        for j in jobs
    ]


@router.get("/{job_id}")
async def get_job(job_id: str):
    job = job_service.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job(payload: JobDescriptionIn):
    result = job_service.analyze_job_description(payload.title, payload.description)
    return JobAnalysisResponse(**result)
