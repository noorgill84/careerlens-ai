"""
Resume improvement suggestions.

HARD RULE (spec §19): never invent companies, metrics, achievements,
technologies, responsibilities, or percentages. Every suggestion here is
either (a) a generic, content-agnostic writing tip, or (b) a pointer to
something the resume is *missing* — never a claim about what the resume
"actually" contains beyond what was extracted.
"""
from __future__ import annotations
import re
from ml.extraction.resume_parser import ResumeProfile
from ml.matching.ats_analyzer import ATSResult

QUANTIFIER_RE = re.compile(r"\d+(\.\d+)?%|\$\d|\b\d{2,}\b")


def generate_suggestions(profile: ResumeProfile, ats_result: ATSResult) -> list[str]:
    suggestions: list[str] = []

    if not profile.summary:
        suggestions.append("Add a 2-3 sentence summary at the top stating your target role and core strengths.")

    for exp in profile.experience:
        if exp.raw_text and not QUANTIFIER_RE.search(exp.raw_text):
            label = exp.position or "an experience entry"
            suggestions.append(
                f"For \"{label}\": describe the measurable outcome (%, time saved, users impacted) if you have one."
            )

    for project in profile.projects:
        text = project.raw_text.lower()
        missing = []
        if "dataset" not in text and "data" not in text:
            missing.append("dataset")
        if not any(k in text for k in ["model", "architecture", "algorithm"]):
            missing.append("model/architecture")
        if not any(k in text for k in ["accuracy", "f1", "metric", "score", "%"]):
            missing.append("evaluation metric")
        if not any(k in text for k in ["deployed", "deployment", "hosted", "live"]):
            missing.append("deployment platform")
        if missing:
            label = project.name or "a project"
            suggestions.append(f"For \"{label}\": consider adding {', '.join(missing)} if applicable.")

    if not profile.certifications:
        suggestions.append("If you've completed any relevant courses or certifications, list them — they strengthen keyword coverage.")

    # fold in ATS analyzer's own structural notes so suggestions aren't duplicated elsewhere
    suggestions.extend(ats_result.notes)

    # de-duplicate while preserving order
    seen = set()
    unique = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique
