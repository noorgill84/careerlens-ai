"""Skill gap analysis: candidate vs target-role skills, with priority tiers."""
from __future__ import annotations
from dataclasses import dataclass, field

# Skills weighted by how commonly they gate interviews for the role family.
# This is a simple, documented heuristic (not learned) — swap for a
# frequency table mined from real job postings once that data exists.
HIGH_PRIORITY_HINTS = {"docker", "kubernetes", "aws", "sql", "git", "system design"}
MEDIUM_PRIORITY_HINTS = {"azure", "gcp", "ci/cd", "redis", "typescript"}


@dataclass
class SkillGapResult:
    have: list[str] = field(default_factory=list)
    missing_high: list[str] = field(default_factory=list)
    missing_medium: list[str] = field(default_factory=list)
    missing_low: list[str] = field(default_factory=list)
    coverage_pct: float = 0.0


_REASONS = {
    "docker": "Containerization is standard for shipping and running production ML/web services.",
    "kubernetes": "Most companies orchestrate production services with Kubernetes at scale.",
    "aws": "The majority of job postings in this field list a cloud platform, most often AWS.",
    "sql": "Nearly every data-adjacent role expects comfort querying relational data.",
    "git": "Version control is assumed baseline knowledge for any engineering role.",
}


def analyze_skill_gap(candidate_skills: list[str], target_skills: list[str]) -> SkillGapResult:
    cand_lower = {s.lower() for s in candidate_skills}
    have = [s for s in target_skills if s.lower() in cand_lower]
    missing = [s for s in target_skills if s.lower() not in cand_lower]

    high, medium, low = [], [], []
    for skill in missing:
        key = skill.lower()
        if key in HIGH_PRIORITY_HINTS:
            high.append(skill)
        elif key in MEDIUM_PRIORITY_HINTS:
            medium.append(skill)
        else:
            low.append(skill)

    coverage = round(100.0 * len(have) / len(target_skills), 1) if target_skills else 100.0

    return SkillGapResult(
        have=have, missing_high=high, missing_medium=medium, missing_low=low, coverage_pct=coverage,
    )


def gap_reason(skill: str) -> str:
    return _REASONS.get(
        skill.lower(),
        f"{skill} appears frequently in postings for this role family and strengthens your fit.",
    )
