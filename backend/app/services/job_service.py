from __future__ import annotations
import re
from ml.extraction.skill_extractor import extract_skills_from_text
from ml.preprocessing.text_cleaning import clean_text
from app.services.sample_jobs import SAMPLE_JOBS

_YEARS_RE = re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?years?", re.I)
_EDU_RE = re.compile(r"\b(bachelor|master|phd|mba|diploma)\b", re.I)


def list_sample_jobs() -> list[dict]:
    return SAMPLE_JOBS


def get_job_by_id(job_id: str) -> dict | None:
    return next((j for j in SAMPLE_JOBS if j["id"] == job_id), None)


def search_jobs(query: str) -> list[dict]:
    """
    Natural-language-ish job search (spec §15).

    True semantic search (embedding the query + job descriptions and
    ranking by cosine similarity) is implemented and used when the
    embedding model is available — see ml/embeddings/embedder.py. When
    it isn't installed/loadable (e.g. this offline dev sandbox), this
    falls back to skill/keyword extraction on the query rather than a
    plain substring match, so a query like "AI jobs involving Python and
    NLP" still matches on the *skills* it names (Python, NLP), not just
    on literal substring hits in the job title.
    """
    if not query.strip():
        return SAMPLE_JOBS

    try:
        from ml.embeddings.embedder import embed_texts, cosine_similarity
        job_texts = [f"{j['title']}. {j['description']}" for j in SAMPLE_JOBS]
        vectors = embed_texts([query] + job_texts)
        query_vec, job_vecs = vectors[0], vectors[1:]
        scored = [(job, cosine_similarity(query_vec, job_vecs[i])) for i, job in enumerate(SAMPLE_JOBS)]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [job for job, score in scored if score > 0.25] or [job for job, _ in scored[:3]]
    except (ImportError, ModuleNotFoundError):
        pass  # embedding model unavailable — fall through to keyword-based ranking below

    query_skills = {s.lower() for s in extract_skills_from_text(query)}
    query_tokens = {t.lower() for t in re.findall(r"[a-zA-Z][a-zA-Z0-9+.#]{2,}", query)}

    def _score(job: dict) -> int:
        job_skills = {s.lower() for s in job["required_skills"] + job.get("preferred_skills", [])}
        skill_hits = len(query_skills & job_skills)
        title_hits = sum(1 for t in query_tokens if t in job["title"].lower())
        return skill_hits * 2 + title_hits

    ranked = sorted(SAMPLE_JOBS, key=_score, reverse=True)
    scored_only = [j for j in ranked if _score(j) > 0]
    return scored_only or SAMPLE_JOBS  # nothing scored — show the full catalog rather than an empty page


def analyze_job_description(title: str, description: str) -> dict:
    text = clean_text(description)
    skills = extract_skills_from_text(text)

    years_match = _YEARS_RE.search(text)
    experience_years = float(years_match.group(1)) if years_match else None

    edu_match = _EDU_RE.search(text)
    education = edu_match.group(1).lower() if edu_match else None

    # naive required/preferred split on common phrasing; anything under a
    # "preferred/nice to have" heading is preferred, else required.
    preferred_section = ""
    split = re.split(r"(preferred|nice to have|bonus)[:\s]", text, flags=re.I, maxsplit=1)
    if len(split) > 1:
        preferred_section = split[-1]
        preferred_skills = extract_skills_from_text(preferred_section)
        required_skills = [s for s in skills if s not in preferred_skills]
    else:
        required_skills = skills
        preferred_skills = []

    keywords = list(dict.fromkeys(re.findall(r"\b[A-Za-z][A-Za-z0-9+.#]{2,}\b", text)))[:40]

    return {
        "title": title,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_years_required": experience_years,
        "education_required": education,
        "keywords": keywords,
    }
