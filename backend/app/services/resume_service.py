"""
Resume service layer: wires the ml/ pipeline to HTTP + storage.

Deliberately thin — all real extraction/scoring logic lives in ml/, so it
stays importable and unit-testable independent of FastAPI (spec §31,
"do not tightly couple the model code to FastAPI").
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass

from ml.extraction.resume_parser import parse_resume, ResumeProfile, UnsupportedFileError, EmptyResumeError, CorruptFileError
from ml.extraction.skill_taxonomy import normalize_skills, NormalizedSkill
from ml.matching.ats_analyzer import analyze_ats, ATSResult
from app.services import db_client
from app.services import improvement_engine
from app.config import settings


class ResumeProcessingError(Exception):
    """Raised for any user-facing resume processing failure (bad file, empty, etc.)."""


@dataclass
class ResumeAnalysisResult:
    resume_id: str
    profile: ResumeProfile
    normalized_skills: list[NormalizedSkill]
    ats_result: ATSResult
    improvement_suggestions: list[str]
    saved: bool = True  # False for anonymous/demo analyses that aren't persisted


def _run_pipeline(file_bytes: bytes, filename: str) -> tuple[ResumeProfile, list[NormalizedSkill], ATSResult, list[str]]:
    try:
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        profile = parse_resume(file_bytes, filename, max_file_size_bytes=max_bytes)
    except (UnsupportedFileError, EmptyResumeError, CorruptFileError, ValueError) as e:
        raise ResumeProcessingError(str(e)) from e

    normalized = normalize_skills(profile.skills_raw)

    ats_result = analyze_ats(
        raw_text=profile.raw_text,
        sections_found=profile.sections_found,
        normalized_skill_count=len(normalized),
        experience_raw_texts=[e.raw_text for e in profile.experience],
        achievements=profile.achievements,
    )

    suggestions = improvement_engine.generate_suggestions(profile, ats_result)
    return profile, normalized, ats_result, suggestions


def process_and_store_resume(*, file_bytes: bytes, filename: str, user_id: str | None) -> ResumeAnalysisResult:
    """
    Runs the full pipeline. If user_id is None (anonymous/demo visitor, spec
    §34), the analysis still runs against the real pipeline but is NOT
    persisted — so the demo produces genuine results without requiring an
    account, while signed-in uploads are saved for the dashboard/history/
    matching features that need a stored resume_id.
    """
    profile, normalized, ats_result, suggestions = _run_pipeline(file_bytes, filename)
    resume_id = str(uuid.uuid4())

    if user_id is not None:
        db_client.save_resume(
            resume_id=resume_id, user_id=user_id, filename=filename, file_bytes=file_bytes,
            profile=profile, normalized_skills=normalized, ats_result=ats_result,
        )

    return ResumeAnalysisResult(
        resume_id=resume_id, profile=profile, normalized_skills=normalized,
        ats_result=ats_result, improvement_suggestions=suggestions, saved=user_id is not None,
    )


def reanalyze_resume(*, resume_id: str, user_id: str) -> ResumeAnalysisResult | None:
    record = db_client.get_resume(resume_id=resume_id, user_id=user_id)
    if record is None:
        return None
    profile, normalized, ats_result, suggestions = _run_pipeline(record["file_bytes"], record["filename"])
    db_client.update_resume_analysis(resume_id=resume_id, profile=profile, normalized_skills=normalized, ats_result=ats_result)
    return ResumeAnalysisResult(
        resume_id=resume_id, profile=profile, normalized_skills=normalized,
        ats_result=ats_result, improvement_suggestions=suggestions,
    )


def delete_resume(*, resume_id: str, user_id: str) -> bool:
    return db_client.delete_resume(resume_id=resume_id, user_id=user_id)
