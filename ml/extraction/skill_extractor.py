"""
Extracts candidate skill mentions from free text.

Approach: scan text for known taxonomy aliases (multi-word aliases matched
first to avoid partial overlaps, e.g. "machine learning" before "machine"),
plus a light heuristic for comma/bullet-separated "Skills:" style lines
which catches skills not yet in the taxonomy (returned unnormalized;
normalize_skills() decides later whether they map to a canonical entry).
"""
from __future__ import annotations
import re
from ml.extraction.skill_taxonomy import CANONICAL_SKILLS, _ALIAS_INDEX  # noqa: F401 (reuse index)

# Sort aliases longest-first so multi-word aliases win over their substrings.
_ALL_ALIASES = sorted(_ALIAS_INDEX.keys(), key=len, reverse=True)
_ALIAS_PATTERNS = [
    (alias, re.compile(r"(?<![a-z0-9])" + re.escape(alias).replace(r"\ ", r"[\s\-]+") + r"(?![a-z0-9])", re.I))
    for alias in _ALL_ALIASES
]


def extract_skills_from_text(text: str) -> list[str]:
    """Return raw (un-deduplicated-by-canonical) skill strings found in text."""
    if not text:
        return []
    found: list[str] = []
    lowered = text.lower()

    for alias, pattern in _ALIAS_PATTERNS:
        if pattern.search(lowered):
            found.append(_ALIAS_INDEX[alias])

    # Also pick up an explicit "Skills:" / bullet list line for anything
    # not in the taxonomy yet, so new/unlisted tech still surfaces.
    for line in text.split("\n"):
        if re.match(r"^\s*(skills?|technologies|tools)\s*[:\-]", line, re.I):
            _, _, rest = line.partition(":")
            tokens = re.split(r"[,•|/]", rest)
            for tok in tokens:
                tok = tok.strip(" .")
                if tok and len(tok) <= 40:
                    found.append(tok)

    # de-duplicate, preserve order
    seen = set()
    unique = []
    for s in found:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique
