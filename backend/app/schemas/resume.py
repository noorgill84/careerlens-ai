from pydantic import BaseModel, Field


class EducationOut(BaseModel):
    institution: str | None = None
    degree: str | None = None
    graduation_year: str | None = None
    gpa: str | None = None


class ExperienceOut(BaseModel):
    company: str | None = None
    position: str | None = None
    duration: str | None = None


class ProjectOut(BaseModel):
    name: str | None = None
    raw_text: str


class SkillOut(BaseModel):
    canonical: str
    category: str | None = None
    matched: bool


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    summary: str | None = None
    education: list[EducationOut] = Field(default_factory=list)
    experience: list[ExperienceOut] = Field(default_factory=list)
    projects: list[ProjectOut] = Field(default_factory=list)
    skills: list[SkillOut] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)

    ats_score: float
    ats_breakdown: dict
    ats_disclaimer: str
    improvement_suggestions: list[str] = Field(default_factory=list)
    saved: bool = True  # False when uploaded anonymously (demo) — not persisted to your account


class ErrorResponse(BaseModel):
    error: str
    message: str
