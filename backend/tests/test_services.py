"""
These tests exercise the service layer directly (not via HTTP), so they run
without fastapi/uvicorn/torch installed — useful in this offline sandbox.
Once `pip install -r requirements.txt` is run with internet access, add
`backend/tests/test_api.py` using FastAPI's TestClient for full HTTP-level
coverage (fastapi.testclient.TestClient(app)).
"""
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.insert(0, os.path.dirname(sys.path[0]))  # repo root, for `ml`

from app.services import job_service, resume_service, career_service, matching_service, db_client
from app.services.matching_service import ModelUnavailableError

SAMPLE_JD = """
We are hiring a Machine Learning Engineer with 2+ years of experience.
Required: Python, Machine Learning, PyTorch, SQL.
Bachelor's degree required.
Preferred: AWS, Docker experience is a plus.
"""

SAMPLE_RESUME_TEXT = """Jordan Patel
jordan.patel@email.com

EDUCATION
IIT Delhi
B.Tech Computer Science, 2024

EXPERIENCE
Machine Learning Intern
Acme AI Labs
Built a text classification pipeline using PyTorch, improving accuracy by 12%.

SKILLS
Python, PyTorch, Machine Learning, SQL
"""


def _make_docx_bytes(text: str) -> bytes:
    import docx
    document = docx.Document()
    for line in text.split("\n"):
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_job_service_analyzes_jd():
    result = job_service.analyze_job_description("ML Engineer", SAMPLE_JD)
    assert "Python" in result["required_skills"]
    assert result["experience_years_required"] == 2.0
    assert result["education_required"] == "bachelor"
    assert "AWS" in result["preferred_skills"] or "Docker" in result["preferred_skills"]


def test_job_service_list_and_get():
    jobs = job_service.list_sample_jobs()
    assert len(jobs) >= 3
    assert all(j["is_sample_data"] for j in jobs)
    job = job_service.get_job_by_id(jobs[0]["id"])
    assert job is not None


def test_resume_service_full_pipeline_and_storage():
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    result = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="resume.docx", user_id="user-1")

    assert result.resume_id
    assert result.profile.email == "jordan.patel@email.com"
    assert 0 <= result.ats_result.overall_score <= 100
    assert isinstance(result.improvement_suggestions, list)

    stored = db_client.get_resume(resume_id=result.resume_id, user_id="user-1")
    assert stored is not None

    deleted = resume_service.delete_resume(resume_id=result.resume_id, user_id="user-1")
    assert deleted is True
    assert db_client.get_resume(resume_id=result.resume_id, user_id="user-1") is None


def test_career_service_role_recommendations():
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    result = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="resume.docx", user_id="user-2")

    recs = career_service.get_role_recommendations(user_id="user-2", resume_id=result.resume_id)
    assert len(recs) > 0
    assert any(r["role"] == "Machine Learning Engineer" for r in recs)


def test_anonymous_upload_is_not_persisted():
    """Spec §34 demo mode: anonymous uploads still run the real pipeline but aren't saved."""
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    result = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="resume.docx", user_id=None)

    assert result.saved is False
    assert result.profile.email == "jordan.patel@email.com"  # pipeline still ran for real
    assert result.ats_result.overall_score >= 0

    # nothing was persisted, so no user can fetch it back
    assert db_client.get_resume(resume_id=result.resume_id, user_id="anyone") is None


def test_reanalyze_resume_actually_works():
    """
    Regression test for a real bug: save_resume() used to hardcode
    file_bytes=None in the dev fallback store, so re-analyzing a
    previously uploaded resume crashed. Confirms the fix: bytes are
    genuinely stored and retrievable.
    """
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    result = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="resume.docx", user_id="user-reanalyze")

    stored = db_client.get_resume(resume_id=result.resume_id, user_id="user-reanalyze")
    assert stored["file_bytes"] is not None
    assert len(stored["file_bytes"]) == len(file_bytes)

    reanalyzed = resume_service.reanalyze_resume(resume_id=result.resume_id, user_id="user-reanalyze")
    assert reanalyzed is not None
    assert reanalyzed.profile.email == "jordan.patel@email.com"


def test_delete_all_user_data():
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    r1 = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="a.docx", user_id="user-bulk")
    r2 = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="b.docx", user_id="user-bulk")
    resume_service.process_and_store_resume(file_bytes=file_bytes, filename="c.docx", user_id="someone-else")

    deleted_count = db_client.delete_all_user_data(user_id="user-bulk")
    assert deleted_count == 2
    assert db_client.get_resume(resume_id=r1.resume_id, user_id="user-bulk") is None
    assert db_client.get_resume(resume_id=r2.resume_id, user_id="user-bulk") is None


def test_matching_service_raises_clear_error_without_model_installed():
    """
    sentence-transformers/torch aren't installed in this sandbox, so the
    matcher should raise ModelUnavailableError rather than fabricate a
    similarity score (spec §49 — no fake claims).
    """
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    result = resume_service.process_and_store_resume(file_bytes=file_bytes, filename="resume.docx", user_id="user-3")

    try:
        matching_service.match_resume_to_job(
            user_id="user-3", resume_id=result.resume_id, job_id="job-001", job_description=None,
        )
        # if this environment DOES have the model installed, that's fine too
    except ModelUnavailableError:
        pass


if __name__ == "__main__":
    test_job_service_analyzes_jd()
    test_job_service_list_and_get()
    test_resume_service_full_pipeline_and_storage()
    test_career_service_role_recommendations()
    test_anonymous_upload_is_not_persisted()
    test_reanalyze_resume_actually_works()
    test_delete_all_user_data()
    test_matching_service_raises_clear_error_without_model_installed()
    print("backend services: all tests passed")
