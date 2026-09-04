"""
Hybrid candidate-job matching engine.

Deliberately NOT cosine-similarity-only (spec §8). Semantic similarity is
one signal among several; skill overlap, experience, education and role
compatibility are computed independently and combined with configurable
weights so the score is explainable and each component can be surfaced
in the UI (spec §18 Explainable AI).

`semantic_similarity` is passed in as a plain float rather than computed
inside this module, so the scoring math can be unit-tested deterministically
without loading the transformer model.
"""
from __future__ import annotations
from dataclasses import dataclass, field

DEFAULT_WEIGHTS: dict[str, float] = {
    "semantic_similarity": 0.35,
    "technical_skills": 0.25,
    "experience": 0.15,
    "education": 0.10,
    "role_compatibility": 0.10,
    "resume_quality": 0.05,
}

assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 1e-9, "weights must sum to 1.0"


@dataclass
class MatchBreakdown:
    overall_score: float  # 0-100
    semantic_similarity: float  # 0-100
    technical_skills: float  # 0-100
    experience: float  # 0-100
    education: float  # 0-100
    role_compatibility: float  # 0-100
    resume_quality: float  # 0-100
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    weights_used: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


def _skill_overlap_score(candidate_skills: list[str], required_skills: list[str]) -> tuple[float, list[str], list[str]]:
    """Score = |intersection| / |required|, case-insensitive canonical-name comparison."""
    if not required_skills:
        return 100.0, [], []
    cand_set = {s.lower() for s in candidate_skills}
    matched = [s for s in required_skills if s.lower() in cand_set]
    missing = [s for s in required_skills if s.lower() not in cand_set]
    score = 100.0 * len(matched) / len(required_skills)
    return round(score, 1), matched, missing


def _experience_score(candidate_years: float, required_years: float) -> float:
    """Full credit at/above requirement; partial credit scaling below it."""
    if required_years <= 0:
        return 100.0
    if candidate_years >= required_years:
        return 100.0
    return round(max(0.0, 100.0 * candidate_years / required_years), 1)


_EDUCATION_RANK = {"phd": 5, "master": 4, "mba": 4, "bachelor": 3, "diploma": 2, "high school": 1}


def _education_score(candidate_level: str | None, required_level: str | None) -> float:
    if not required_level:
        return 100.0
    if not candidate_level:
        return 40.0  # unknown education isn't automatically zero — avoid penalizing extraction gaps too harshly
    cand_rank = _EDUCATION_RANK.get(candidate_level.lower(), 3)
    req_rank = _EDUCATION_RANK.get(required_level.lower(), 3)
    if cand_rank >= req_rank:
        return 100.0
    diff = req_rank - cand_rank
    return round(max(0.0, 100.0 - diff * 25.0), 1)


def _role_compatibility_score(candidate_titles: list[str], target_role: str) -> float:
    """Lightweight lexical overlap between past titles and the target role name."""
    if not target_role:
        return 100.0
    target_tokens = set(target_role.lower().split())
    if not candidate_titles:
        return 30.0
    best = 0.0
    for title in candidate_titles:
        title_tokens = set(title.lower().split())
        if not title_tokens:
            continue
        overlap = len(target_tokens & title_tokens) / len(target_tokens)
        best = max(best, overlap)
    return round(min(100.0, best * 100.0), 1)


def compute_hybrid_match(
    *,
    semantic_similarity: float,       # 0-1, from embedder.cosine_similarity
    candidate_skills: list[str],
    required_skills: list[str],
    candidate_years_experience: float,
    required_years_experience: float,
    candidate_education_level: str | None,
    required_education_level: str | None,
    candidate_titles: list[str],
    target_role: str,
    resume_quality_score: float,      # 0-100, from ats_analyzer
    weights: dict[str, float] | None = None,
) -> MatchBreakdown:
    """Combine independent sub-scores into a single explainable 0-100 match."""
    w = weights or DEFAULT_WEIGHTS
    if abs(sum(w.values()) - 1.0) > 1e-6:
        raise ValueError(f"weights must sum to 1.0, got {sum(w.values())}")

    semantic_pct = round(max(0.0, min(1.0, semantic_similarity)) * 100.0, 1)
    skills_pct, matched, missing = _skill_overlap_score(candidate_skills, required_skills)
    experience_pct = _experience_score(candidate_years_experience, required_years_experience)
    education_pct = _education_score(candidate_education_level, required_education_level)
    role_pct = _role_compatibility_score(candidate_titles, target_role)
    quality_pct = round(max(0.0, min(100.0, resume_quality_score)), 1)

    overall = (
        semantic_pct * w["semantic_similarity"]
        + skills_pct * w["technical_skills"]
        + experience_pct * w["experience"]
        + education_pct * w["education"]
        + role_pct * w["role_compatibility"]
        + quality_pct * w["resume_quality"]
    )

    return MatchBreakdown(
        overall_score=round(overall, 1),
        semantic_similarity=semantic_pct,
        technical_skills=skills_pct,
        experience=experience_pct,
        education=education_pct,
        role_compatibility=role_pct,
        resume_quality=quality_pct,
        matched_skills=matched,
        missing_skills=missing,
        weights_used=dict(w),
    )


def explain_match(breakdown: MatchBreakdown, top_n_reasons: int = 4) -> dict[str, list[str]]:
    """Turn the numeric breakdown into human-readable strengths/gaps (spec §18)."""
    components = [
        ("Semantic profile alignment", breakdown.semantic_similarity),
        ("Technical skill coverage", breakdown.technical_skills),
        ("Experience level", breakdown.experience),
        ("Education fit", breakdown.education),
        ("Role compatibility", breakdown.role_compatibility),
        ("Resume quality", breakdown.resume_quality),
    ]
    strengths = [f"Strong {name.lower()} ({score:.0f}%)" for name, score in components if score >= 75]
    gaps = [f"{name} could be stronger ({score:.0f}%)" for name, score in components if score < 60]
    if breakdown.matched_skills:
        strengths.append(f"Matches {len(breakdown.matched_skills)} required skill(s): " + ", ".join(breakdown.matched_skills[:5]))
    if breakdown.missing_skills:
        gaps.append("Missing: " + ", ".join(breakdown.missing_skills[:5]))
    return {"strengths": strengths[:top_n_reasons], "gaps": gaps[:top_n_reasons]}
