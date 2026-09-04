"""
Career role recommendation.

Ranks a small catalog of role profiles (each defined by its typical
required skills) against the candidate's normalized skill set + resume
embedding. Semantic similarity is injected per-role by the caller (from
embedder.cosine_similarity against a precomputed role-description
embedding) so this module stays testable without loading the model.
"""
from __future__ import annotations
from dataclasses import dataclass, field

ROLE_CATALOG: dict[str, list[str]] = {
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "SQL", "Docker"],
    "Data Scientist": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "Scikit-learn"],
    "AI Engineer": ["Python", "Deep Learning", "Natural Language Processing", "Hugging Face Transformers", "Docker"],
    "Data Analyst": ["SQL", "Pandas", "Python", "Communication"],
    "Backend Engineer": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "AWS"],
    "Full-Stack Engineer": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "Git"],
    "Frontend Engineer": ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Git"],
}


@dataclass
class RoleRecommendation:
    role: str
    compatibility: float  # 0-100
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    reason: str = ""


def recommend_roles(
    candidate_skills: list[str],
    semantic_scores: dict[str, float] | None = None,  # role -> 0-1 similarity, optional
    top_k: int = 5,
) -> list[RoleRecommendation]:
    cand_lower = {s.lower() for s in candidate_skills}
    results = []
    for role, required in ROLE_CATALOG.items():
        matched = [s for s in required if s.lower() in cand_lower]
        missing = [s for s in required if s.lower() not in cand_lower]
        skill_score = 100.0 * len(matched) / len(required) if required else 0.0
        semantic = (semantic_scores or {}).get(role)
        compatibility = round(0.7 * skill_score + 0.3 * (semantic * 100 if semantic is not None else skill_score), 1)

        reason_parts = []
        if matched:
            reason_parts.append(f"you already have {', '.join(matched[:3])}")
        if missing:
            reason_parts.append(f"adding {', '.join(missing[:2])} would strengthen this fit")
        reason = "Recommended because " + "; ".join(reason_parts) + "." if reason_parts else "Based on your overall skill profile."

        results.append(RoleRecommendation(
            role=role, compatibility=compatibility, matched_skills=matched, missing_skills=missing, reason=reason,
        ))

    results.sort(key=lambda r: r.compatibility, reverse=True)
    return results[:top_k]
