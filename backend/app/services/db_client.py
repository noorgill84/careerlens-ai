"""
Database + file storage access layer.

Uses `supabase-py` against Postgres (schema: supabase/schema.sql) for
records, and Supabase Storage (bucket: "resumes") for the original
uploaded file bytes, when SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY are
configured. When they are NOT configured (e.g. running this backend
locally without a Supabase project yet), falls back to a process-local
in-memory store — including the actual file bytes, not a placeholder —
so /api/resume/analyze/{id} (re-analyze) genuinely works in dev too.
This fallback is explicitly NOT for production (data vanishes on
restart, no multi-instance support, no RLS). Swap points are isolated to
this file; callers never know which backend is active.

Storage bucket setup: run `python backend/scripts/setup_storage_bucket.py`
once against your Supabase project (see that file for details) before
first use in production — it creates the private "resumes" bucket if
it doesn't already exist.
"""
from __future__ import annotations
from dataclasses import asdict
from app.config import settings

_memory_resumes: dict[str, dict] = {}  # dev-only fallback store, holds real file_bytes
STORAGE_BUCKET = "resumes"


def _use_supabase() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY)


def _get_supabase_client():
    from supabase import create_client
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def save_resume(*, resume_id: str, user_id: str, filename: str, file_bytes: bytes, profile, normalized_skills, ats_result) -> None:
    if _use_supabase():
        client = _get_supabase_client()
        storage_path = f"{user_id}/{resume_id}/{filename}"
        client.storage.from_(STORAGE_BUCKET).upload(
            storage_path, file_bytes, file_options={"content-type": "application/octet-stream"}
        )
        record = {
            "id": resume_id,
            "user_id": user_id,
            "filename": filename,
            "storage_path": storage_path,
            "extracted_profile": asdict(profile),
            "ats_score": ats_result.overall_score,
        }
        client.table("resumes").insert(record).execute()
        client.table("resume_analysis").insert({
            "resume_id": resume_id,
            "ats_breakdown": {
                "formatting": ats_result.formatting,
                "keyword_optimization": ats_result.keyword_optimization,
                "skills_coverage": ats_result.skills_coverage,
                "experience_quality": ats_result.experience_quality,
                "achievements": ats_result.achievements,
                "structure": ats_result.structure,
            },
        }).execute()
    else:
        _memory_resumes[resume_id] = {
            "id": resume_id,
            "user_id": user_id,
            "filename": filename,
            "file_bytes": file_bytes,  # real bytes, so reanalyze actually works in dev
            "extracted_profile": asdict(profile),
            "normalized_skills": [asdict(s) for s in normalized_skills],
            "ats_score": ats_result.overall_score,
        }


def get_resume(*, resume_id: str, user_id: str) -> dict | None:
    if _use_supabase():
        client = _get_supabase_client()
        res = client.table("resumes").select("*").eq("id", resume_id).eq("user_id", user_id).single().execute()
        if not res.data:
            return None
        record = dict(res.data)
        storage_path = record.get("storage_path")
        if storage_path:
            try:
                record["file_bytes"] = client.storage.from_(STORAGE_BUCKET).download(storage_path)
            except Exception:
                # File may have been removed from storage independently of the DB row;
                # surface a record with no bytes rather than crashing the whole read.
                record["file_bytes"] = None
        return record
    record = _memory_resumes.get(resume_id)
    if record and record["user_id"] == user_id:
        return record
    return None


def update_resume_analysis(*, resume_id: str, profile, normalized_skills, ats_result) -> None:
    if _use_supabase():
        client = _get_supabase_client()
        client.table("resumes").update({
            "extracted_profile": asdict(profile), "ats_score": ats_result.overall_score,
        }).eq("id", resume_id).execute()
    elif resume_id in _memory_resumes:
        _memory_resumes[resume_id]["extracted_profile"] = asdict(profile)
        _memory_resumes[resume_id]["normalized_skills"] = [asdict(s) for s in normalized_skills]
        _memory_resumes[resume_id]["ats_score"] = ats_result.overall_score


def delete_all_user_data(*, user_id: str) -> int:
    """Delete every resume (and cascading analyses, via FK ON DELETE CASCADE
    in supabase/schema.sql) owned by this user. Returns count deleted."""
    if _use_supabase():
        client = _get_supabase_client()
        existing = client.table("resumes").select("id, storage_path").eq("user_id", user_id).execute()
        paths = [r["storage_path"] for r in (existing.data or []) if r.get("storage_path")]
        if paths:
            client.storage.from_(STORAGE_BUCKET).remove(paths)
        res = client.table("resumes").delete().eq("user_id", user_id).execute()
        return len(res.data or [])
    to_delete = [rid for rid, rec in _memory_resumes.items() if rec["user_id"] == user_id]
    for rid in to_delete:
        del _memory_resumes[rid]
    return len(to_delete)


def delete_resume(*, resume_id: str, user_id: str) -> bool:
    if _use_supabase():
        client = _get_supabase_client()
        existing = client.table("resumes").select("storage_path").eq("id", resume_id).eq("user_id", user_id).single().execute()
        if existing.data and existing.data.get("storage_path"):
            client.storage.from_(STORAGE_BUCKET).remove([existing.data["storage_path"]])
        res = client.table("resumes").delete().eq("id", resume_id).eq("user_id", user_id).execute()
        return bool(res.data)
    if resume_id in _memory_resumes and _memory_resumes[resume_id]["user_id"] == user_id:
        del _memory_resumes[resume_id]
        return True
    return False
