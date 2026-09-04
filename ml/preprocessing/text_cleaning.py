"""Text cleaning shared by resume and job-description pipelines."""
from __future__ import annotations
import re

BULLET_CHARS = "•◦▪‣∙·●○*-–—"


def clean_text(raw: str) -> str:
    """Normalize whitespace, de-hyphenate line-wrapped words, strip bullets."""
    if not raw:
        return ""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # de-hyphenate words split across a line break, e.g. "develop-\nment"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # collapse runs of blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # strip common bullet characters at line starts
    text = re.sub(rf"^[{re.escape(BULLET_CHARS)}]+\s*", "", text, flags=re.MULTILINE)
    # collapse horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_/]+", re.I)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+", re.I)
URL_RE = re.compile(r"https?://[^\s)]+")


def extract_contact_fields(text: str) -> dict:
    email = EMAIL_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)
    # phone: search only first ~15 lines to avoid picking numbers from body text
    header = "\n".join(split_lines(text)[:15])
    phone = PHONE_RE.search(header)
    phone_val = phone.group(0).strip() if phone and len(re.sub(r"\D", "", phone.group(0))) >= 7 else None

    portfolio = None
    for url in URL_RE.findall(text):
        if "linkedin.com" not in url and "github.com" not in url:
            portfolio = url
            break

    return {
        "email": email.group(0) if email else None,
        "phone": phone_val,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "portfolio": portfolio,
    }
