"""
ATS-style resume analyzer.

IMPORTANT: this is explicitly an *ATS-style heuristic analysis*, not a
real commercial ATS (Workday, Greenhouse, Taleo, etc.), which use
proprietary and often opaque scoring. We say so in the API response
(`disclaimer` field) so the product never overstates what it does.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

QUANTIFIER_PATTERN = re.compile(r"\b\d+(\.\d+)?%|\$\d|\b\d{2,}\b")
ACTION_VERBS = {
    "built", "designed", "developed", "implemented", "led", "managed", "created",
    "optimized", "improved", "reduced", "increased", "automated", "deployed",
    "architected", "launched", "delivered", "analyzed", "engineered",
}


@dataclass
class ATSResult:
    overall_score: float
    formatting: float
    keyword_optimization: float
    skills_coverage: float
    experience_quality: float
    achievements: float
    structure: float
    disclaimer: str = "This is an ATS-style analysis, not a score from a commercial ATS product."
    notes: list[str] = field(default_factory=list)


def _score_structure(sections_found: list[str]) -> tuple[float, list[str]]:
    expected = {"header", "education", "experience", "skills"}
    present = expected & set(sections_found)
    score = 100.0 * len(present) / len(expected)
    notes = []
    missing = expected - present
    if missing:
        notes.append(f"Consider adding clearly labeled section(s): {', '.join(sorted(missing))}.")
    return round(score, 1), notes


def _score_formatting(raw_text: str) -> tuple[float, list[str]]:
    notes = []
    score = 100.0
    line_lengths = [len(l) for l in raw_text.split("\n") if l.strip()]
    if line_lengths and max(line_lengths) > 200:
        score -= 15
        notes.append("Some lines are unusually long — check for a broken table/column layout.")
    if len(raw_text) < 400:
        score -= 20
        notes.append("Resume content seems short; ATS systems favor sufficiently detailed resumes.")
    return round(max(0.0, score), 1), notes


def _score_keyword_optimization(matched_skill_count: int, target_skill_count: int) -> tuple[float, list[str]]:
    if target_skill_count == 0:
        return 70.0, ["Paste a target job description for keyword-specific scoring."]
    score = round(100.0 * min(1.0, matched_skill_count / target_skill_count), 1)
    notes = []
    if score < 60:
        notes.append("Resume keywords cover less than 60% of the target job's key terms.")
    return score, notes


def _score_skills_coverage(skill_count: int) -> tuple[float, list[str]]:
    # heuristic: 8+ distinct normalized skills reads as solid coverage
    score = round(min(100.0, (skill_count / 8.0) * 100.0), 1)
    notes = [] if skill_count >= 5 else ["List more specific technical skills (aim for 8+)."]
    return score, notes


def _score_experience_quality(experience_raw_texts: list[str]) -> tuple[float, list[str]]:
    if not experience_raw_texts:
        return 50.0, ["No experience/internship section detected."]
    verb_hits = 0
    total = len(experience_raw_texts)
    for block in experience_raw_texts:
        lower = block.lower()
        if any(re.search(rf"\b{v}\b", lower) for v in ACTION_VERBS):
            verb_hits += 1
    score = round(100.0 * verb_hits / total, 1)
    notes = [] if score >= 70 else ["Start bullet points with strong action verbs (built, led, optimized...)."]
    return score, notes


def _score_achievements(experience_raw_texts: list[str], achievements: list[str]) -> tuple[float, list[str]]:
    text_blob = " ".join(experience_raw_texts) + " " + " ".join(achievements)
    quantified = len(QUANTIFIER_PATTERN.findall(text_blob))
    denom = max(1, len(experience_raw_texts) + len(achievements))
    score = round(min(100.0, (quantified / denom) * 100.0), 1)
    notes = [] if score >= 50 else ["Add measurable outcomes (%, counts, time saved) to bullet points."]
    return score, notes


def analyze_ats(
    *,
    raw_text: str,
    sections_found: list[str],
    normalized_skill_count: int,
    experience_raw_texts: list[str],
    achievements: list[str],
    target_skills: list[str] | None = None,
    matched_target_skills: int = 0,
) -> ATSResult:
    structure, n1 = _score_structure(sections_found)
    formatting, n2 = _score_formatting(raw_text)
    keywords, n3 = _score_keyword_optimization(matched_target_skills, len(target_skills or []))
    skills_cov, n4 = _score_skills_coverage(normalized_skill_count)
    exp_quality, n5 = _score_experience_quality(experience_raw_texts)
    achievements_score, n6 = _score_achievements(experience_raw_texts, achievements)

    overall = round(
        formatting * 0.15 + keywords * 0.20 + skills_cov * 0.20
        + exp_quality * 0.20 + achievements_score * 0.15 + structure * 0.10,
        1,
    )

    return ATSResult(
        overall_score=overall,
        formatting=formatting,
        keyword_optimization=keywords,
        skills_coverage=skills_cov,
        experience_quality=exp_quality,
        achievements=achievements_score,
        structure=structure,
        notes=n1 + n2 + n3 + n4 + n5 + n6,
    )
