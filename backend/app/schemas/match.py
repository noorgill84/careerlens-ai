from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    job_description: str | None = None  # allow ad-hoc JD text instead of a stored job


class MatchBreakdownOut(BaseModel):
    overall_score: float
    semantic_similarity: float
    technical_skills: float
    experience: float
    education: float
    role_compatibility: float
    resume_quality: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class MatchResponse(BaseModel):
    breakdown: MatchBreakdownOut
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
