from pydantic import BaseModel, Field


class JobDescriptionIn(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=20, max_length=20000)


class JobAnalysisResponse(BaseModel):
    title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_years_required: float | None = None
    education_required: str | None = None
    keywords: list[str] = Field(default_factory=list)


class JobSummary(BaseModel):
    id: str
    title: str
    company: str
    location: str | None = None
    is_sample_data: bool = True
    required_skills: list[str] = Field(default_factory=list)
