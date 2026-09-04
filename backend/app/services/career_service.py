from __future__ import annotations
from ml.recommendation.role_recommender import recommend_roles
from ml.recommendation.skill_gap import analyze_skill_gap, gap_reason
from app.services import db_client, job_service


def get_role_recommendations(*, user_id: str, resume_id: str) -> list[dict]:
    record = db_client.get_resume(resume_id=resume_id, user_id=user_id)
    if record is None:
        raise ValueError("Resume not found.")
    candidate_skills = [s["canonical"] for s in record["normalized_skills"]]
    recs = recommend_roles(candidate_skills)
    return [
        {
            "role": r.role, "compatibility": r.compatibility,
            "matched_skills": r.matched_skills, "missing_skills": r.missing_skills, "reason": r.reason,
        }
        for r in recs
    ]


def get_skill_gap(*, user_id: str, resume_id: str, job_id: str) -> dict:
    record = db_client.get_resume(resume_id=resume_id, user_id=user_id)
    if record is None:
        raise ValueError("Resume not found.")
    job = job_service.get_job_by_id(job_id)
    if job is None:
        raise ValueError("Job not found.")

    candidate_skills = [s["canonical"] for s in record["normalized_skills"]]
    result = analyze_skill_gap(candidate_skills, job["required_skills"])
    return {
        "have": result.have,
        "missing_high_priority": [{"skill": s, "reason": gap_reason(s)} for s in result.missing_high],
        "missing_medium_priority": [{"skill": s, "reason": gap_reason(s)} for s in result.missing_medium],
        "missing_low_priority": [{"skill": s, "reason": gap_reason(s)} for s in result.missing_low],
        "coverage_pct": result.coverage_pct,
    }
