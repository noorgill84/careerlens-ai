from __future__ import annotations
from ml.matching.hybrid_matcher import compute_hybrid_match, explain_match
from app.services import db_client, job_service


class ModelUnavailableError(Exception):
    """Raised when the transformer embedding model isn't installed/loadable.

    We deliberately raise rather than silently falling back to a fake
    similarity number — showing a clear 'model unavailable' error is more
    honest than a plausible-looking score that isn't real (spec §49).
    """


def _get_embedding_similarity(resume_text: str, job_text: str) -> float:
    from ml.embeddings.embedder import embed_texts, cosine_similarity  # module import is always safe (lazy-loads torch)
    try:
        vectors = embed_texts([resume_text, job_text])
    except (ImportError, ModuleNotFoundError) as e:
        raise ModelUnavailableError(
            "sentence-transformers is not installed on this server. "
            "Install backend/requirements.txt in an environment with internet access."
        ) from e
    return cosine_similarity(vectors[0], vectors[1])


def match_resume_to_job(*, user_id: str, resume_id: str, job_id: str | None, job_description: str | None) -> dict:
    resume_record = db_client.get_resume(resume_id=resume_id, user_id=user_id)
    if resume_record is None:
        raise ValueError("Resume not found.")

    profile_dict = resume_record["extracted_profile"]
    candidate_skills = [s["canonical"] for s in resume_record["normalized_skills"]]
    resume_text = profile_dict.get("raw_text", "")

    if job_id:
        job = job_service.get_job_by_id(job_id)
        if job is None:
            raise ValueError("Job not found.")
        job_text = job["description"]
        required_skills = job["required_skills"]
        target_role = job["title"]
        required_years = job.get("experience_years_required") or 0
        required_education = job.get("education_required")
    elif job_description:
        analyzed = job_service.analyze_job_description("Custom Job", job_description)
        job_text = job_description
        required_skills = analyzed["required_skills"]
        target_role = "Custom Job"
        required_years = analyzed["experience_years_required"] or 0
        required_education = analyzed["education_required"]
    else:
        raise ValueError("Either job_id or job_description must be provided.")

    semantic_similarity = _get_embedding_similarity(resume_text, job_text)

    candidate_titles = [e.get("position") for e in profile_dict.get("experience", []) if e.get("position")]
    candidate_years = len(profile_dict.get("experience", []))  # heuristic proxy; refine with real date parsing
    candidate_education = profile_dict.get("education", [{}])[0].get("degree") if profile_dict.get("education") else None

    breakdown = compute_hybrid_match(
        semantic_similarity=semantic_similarity,
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        candidate_years_experience=candidate_years,
        required_years_experience=required_years,
        candidate_education_level=candidate_education,
        required_education_level=required_education,
        candidate_titles=candidate_titles,
        target_role=target_role,
        resume_quality_score=resume_record.get("ats_score", 70),
    )
    explanation = explain_match(breakdown)
    return {"breakdown": breakdown, **explanation}
