"""
Skill taxonomy & normalization.

Maps messy, real-world skill strings (as they actually appear on resumes)
to a canonical skill name + category. This is intentionally a plain-Python
dict-based system (not ML) because normalization is a lookup/rules problem,
not a learning problem — using a model here would be over-engineering.

Extending the taxonomy: add aliases to CANONICAL_SKILLS. Keys are the
canonical name shown to the user; values are (category, [aliases]).
Matching is case-insensitive and punctuation/whitespace-insensitive.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

CANONICAL_SKILLS: dict[str, tuple[str, list[str]]] = {
    # Languages
    "Python": ("Programming Language", ["python", "python3", "py"]),
    "JavaScript": ("Programming Language", ["javascript", "js", "es6", "ecmascript"]),
    "TypeScript": ("Programming Language", ["typescript", "ts"]),
    "Java": ("Programming Language", ["java"]),
    "C++": ("Programming Language", ["c++", "cpp", "c plus plus"]),
    "C": ("Programming Language", ["c programming", " c "]),
    "SQL": ("Programming Language", ["sql", "structured query language"]),
    "Go": ("Programming Language", ["golang", "go lang"]),
    "R": ("Programming Language", ["r programming", "r language"]),

    # Frontend
    "React": ("Framework", ["react.js", "react js", "reactjs", "react"]),
    "Next.js": ("Framework", ["next.js", "nextjs", "next js"]),
    "Vue.js": ("Framework", ["vue.js", "vuejs", "vue"]),
    "Angular": ("Framework", ["angular.js", "angularjs", "angular"]),
    "Tailwind CSS": ("Framework", ["tailwindcss", "tailwind css", "tailwind"]),

    # Backend
    "Node.js": ("Framework", ["node.js", "nodejs", "node js", "node"]),
    "FastAPI": ("Framework", ["fastapi", "fast api"]),
    "Django": ("Framework", ["django"]),
    "Flask": ("Framework", ["flask"]),
    "Spring Boot": ("Framework", ["spring boot", "springboot", "spring"]),
    "Express.js": ("Framework", ["express.js", "expressjs", "express js", "express"]),

    # AI / ML
    "Machine Learning": ("AI/ML", ["machine learning", "ml", "machine-learning"]),
    "Deep Learning": ("AI/ML", ["deep learning", "dl", "deep-learning"]),
    "Natural Language Processing": ("AI/ML", ["nlp", "natural language processing"]),
    "Computer Vision": ("AI/ML", ["computer vision", "cv", "opencv based vision"]),
    "PyTorch": ("AI/ML", ["pytorch", "py torch"]),
    "TensorFlow": ("AI/ML", ["tensorflow", "tensor flow", "tf"]),
    "Scikit-learn": ("AI/ML", ["scikit-learn", "sklearn", "scikit learn"]),
    "Hugging Face Transformers": ("AI/ML", ["huggingface", "hugging face", "transformers library"]),
    "Sentence Transformers": ("AI/ML", ["sentence transformers", "sentence-transformers", "sbert"]),

    # Data
    "Pandas": ("Data", ["pandas"]),
    "NumPy": ("Data", ["numpy"]),
    "PostgreSQL": ("Database", ["postgresql", "postgres", "psql"]),
    "MongoDB": ("Database", ["mongodb", "mongo"]),
    "MySQL": ("Database", ["mysql"]),
    "Redis": ("Database", ["redis"]),

    # Cloud / DevOps
    "AWS": ("Cloud", ["aws", "amazon web services"]),
    "Azure": ("Cloud", ["azure", "microsoft azure"]),
    "Google Cloud Platform": ("Cloud", ["gcp", "google cloud platform", "google cloud"]),
    "Docker": ("DevOps", ["docker"]),
    "Kubernetes": ("DevOps", ["kubernetes", "k8s"]),
    "CI/CD": ("DevOps", ["ci/cd", "cicd", "continuous integration"]),
    "Git": ("DevOps", ["git", "github", "gitlab", "version control"]),

    # Soft skills
    "Communication": ("Soft Skill", ["communication", "communication skills"]),
    "Leadership": ("Soft Skill", ["leadership", "team leadership"]),
    "Problem Solving": ("Soft Skill", ["problem solving", "problem-solving"]),
    "Teamwork": ("Soft Skill", ["teamwork", "collaboration", "team player"]),
}

# Reverse index: normalized alias string -> canonical name, built once at import.
_ALIAS_INDEX: dict[str, str] = {}
for canonical, (_category, aliases) in CANONICAL_SKILLS.items():
    _ALIAS_INDEX[_normalize_key := canonical.strip().lower()] = canonical
    for alias in aliases:
        _ALIAS_INDEX[alias.strip().lower()] = canonical


def _clean(raw: str) -> str:
    """Lowercase, strip punctuation noise, collapse whitespace."""
    s = raw.strip().lower()
    s = re.sub(r"[_\-]+", " ", s)          # react-js / machine_learning -> spaced
    s = re.sub(r"[^a-z0-9+.# ]", " ", s)   # keep +, ., # for C++/Node.js/C#
    s = re.sub(r"\s+", " ", s).strip()
    return s


@dataclass
class NormalizedSkill:
    raw: str
    canonical: Optional[str]
    category: Optional[str]
    matched: bool


def normalize_skill(raw_skill: str) -> NormalizedSkill:
    """Map a raw skill string to its canonical form, if known."""
    cleaned = _clean(raw_skill)
    if cleaned in _ALIAS_INDEX:
        canonical = _ALIAS_INDEX[cleaned]
        category = CANONICAL_SKILLS[canonical][0]
        return NormalizedSkill(raw=raw_skill, canonical=canonical, category=category, matched=True)

    # try loose match: alias without spaces (e.g. "reactjs" vs "react js")
    cleaned_nospace = cleaned.replace(" ", "")
    for alias, canonical in _ALIAS_INDEX.items():
        if alias.replace(" ", "") == cleaned_nospace:
            category = CANONICAL_SKILLS[canonical][0]
            return NormalizedSkill(raw=raw_skill, canonical=canonical, category=category, matched=True)

    # unknown skill: keep as-is (title-cased), category unknown.
    return NormalizedSkill(raw=raw_skill, canonical=raw_skill.strip(), category=None, matched=False)


def normalize_skills(raw_skills: list[str]) -> list[NormalizedSkill]:
    """Normalize a list, de-duplicating by canonical name."""
    seen: dict[str, NormalizedSkill] = {}
    for raw in raw_skills:
        if not raw or not raw.strip():
            continue
        result = normalize_skill(raw)
        key = (result.canonical or result.raw).lower()
        if key not in seen:
            seen[key] = result
    return list(seen.values())
