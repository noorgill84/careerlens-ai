"""
HTTP-level tests using FastAPI's TestClient — these exercise real routes,
auth enforcement, and request validation (not just the service layer).

Requires `pip install -r backend/requirements.txt` (fastapi, httpx) —
NOT run in the offline dev sandbox this project was built in, since fastapi
isn't installed there. Run with:
    cd backend && PYTHONPATH=..:. pytest tests/test_api.py -v
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(sys.path[0]))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _make_docx_bytes(text: str) -> bytes:
    import docx
    document = docx.Document()
    for line in text.split("\n"):
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


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


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_jobs_is_public_and_labeled_as_sample():
    res = client.get("/api/jobs")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) >= 3
    assert all(j["is_sample_data"] for j in jobs)


def test_job_search_query_param():
    res = client.get("/api/jobs?q=python machine learning")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_analyze_job_description_public_endpoint():
    payload = {
        "title": "ML Engineer",
        "description": "We need 2+ years experience with Python, PyTorch and SQL. Bachelor's required.",
    }
    res = client.post("/api/jobs/analyze", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "Python" in body["required_skills"]
    assert body["experience_years_required"] == 2.0


def test_analyze_job_description_rejects_short_description():
    res = client.post("/api/jobs/analyze", json={"title": "X", "description": "too short"})
    assert res.status_code == 422  # Pydantic min_length validation


def test_anonymous_resume_upload_succeeds_but_is_not_saved():
    """Spec §34 — demo mode works without an Authorization header."""
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    res = client.post(
        "/api/resume/upload",
        files={"file": ("resume.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["saved"] is False
    assert body["email"] == "jordan.patel@email.com"


def test_resume_upload_rejects_unsupported_file_type():
    res = client.post("/api/resume/upload", files={"file": ("resume.txt", b"hello world", "text/plain")})
    assert res.status_code == 422


def test_protected_route_rejects_missing_auth():
    res = client.delete("/api/resume/some-id")
    assert res.status_code == 401


def test_protected_route_rejects_garbage_token():
    res = client.get("/api/history", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_match_endpoint_requires_auth():
    res = client.post("/api/match", json={"resume_id": "x", "job_id": "job-001"})
    assert res.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
