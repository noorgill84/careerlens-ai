"""
Detects resume sections (Education, Experience, Projects, Skills, etc.)
using heading heuristics. Real resumes vary wildly in formatting, so this
is deliberately rule-based and permissive rather than a trained classifier —
a small labeled dataset for section classification is rarely available,
and heading-based rules generalize better with zero training data.
"""
from __future__ import annotations
import re
from ml.preprocessing.text_cleaning import split_lines

SECTION_ALIASES: dict[str, list[str]] = {
    "summary": ["summary", "objective", "profile", "about"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "employment", "professional experience", "internship", "internships"],
    "projects": ["projects", "academic projects", "personal projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
}

_MAX_HEADING_WORDS = 5


def _match_section(line: str) -> str | None:
    normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
    if not normalized or len(normalized.split()) > _MAX_HEADING_WORDS:
        return None
    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias or normalized.startswith(alias):
                return section
    return None


def detect_sections(text: str) -> dict[str, str]:
    """Return {section_name: section_text}. Unmatched leading text -> 'header'."""
    lines = split_lines(text)
    sections: dict[str, list[str]] = {"header": []}
    current = "header"

    for line in lines:
        matched = _match_section(line)
        # a heading line is usually short, often ALL CAPS or Title Case, on its own
        looks_like_heading = matched is not None and (
            line.isupper() or line.istitle() or len(line.split()) <= _MAX_HEADING_WORDS
        )
        if looks_like_heading:
            current = matched
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
