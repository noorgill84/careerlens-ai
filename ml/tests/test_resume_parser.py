import io
from ml.extraction.resume_parser import parse_resume, EmptyResumeError, UnsupportedFileError

SAMPLE_RESUME_TEXT = """Jordan Patel
jordan.patel@email.com | +1 555 123 4567
linkedin.com/in/jordanpatel | github.com/jordanpatel

SUMMARY
Aspiring machine learning engineer with hands-on project experience in NLP and computer vision.

EDUCATION
Indian Institute of Technology
B.Tech Computer Science, 2024
CGPA: 8.7/10

EXPERIENCE
Machine Learning Intern
Acme AI Labs
Jun 2023 - Aug 2023
Built a text classification pipeline using PyTorch, improving accuracy by 12%.
Automated the data preprocessing workflow, reducing manual effort by 40%.

PROJECTS
Resume Matching Engine
Built a semantic job-matching prototype using Sentence Transformers and FastAPI.

SKILLS
Python, PyTorch, Machine Learning, SQL, Docker, React

CERTIFICATIONS
Deep Learning Specialization

ACHIEVEMENTS
Won 1st place in university AI hackathon
"""


def _make_docx_bytes(text: str) -> bytes:
    import docx
    document = docx.Document()
    for line in text.split("\n"):
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_parses_docx_end_to_end():
    file_bytes = _make_docx_bytes(SAMPLE_RESUME_TEXT)
    profile = parse_resume(file_bytes, "resume.docx")

    assert profile.email == "jordan.patel@email.com"
    assert profile.linkedin and "jordanpatel" in profile.linkedin
    assert profile.github and "jordanpatel" in profile.github
    assert "python" in [s.lower() for s in profile.skills_raw]
    assert "pytorch" in [s.lower() for s in profile.skills_raw]
    assert len(profile.education) >= 1
    assert len(profile.experience) >= 1
    assert len(profile.projects) >= 1
    assert "Deep Learning Specialization" in profile.certifications
    assert any("hackathon" in a.lower() for a in profile.achievements)


def test_empty_file_raises():
    try:
        parse_resume(b"", "resume.docx")
        assert False, "should have raised"
    except EmptyResumeError:
        pass


def test_unsupported_extension_raises():
    try:
        parse_resume(b"hello world", "resume.txt")
        assert False, "should have raised"
    except UnsupportedFileError:
        pass


if __name__ == "__main__":
    test_parses_docx_end_to_end()
    test_empty_file_raises()
    test_unsupported_extension_raises()
    print("resume_parser: all tests passed")
