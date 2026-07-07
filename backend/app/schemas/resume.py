from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeOut(BaseModel):
    """Lightweight shape used for the resume list (GET /resumes)."""

    id: int
    filename: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetail(BaseModel):
    """Full shape returned after upload and from GET /resumes/{id} — includes parsed sections."""

    id: int
    filename: str
    uploaded_at: datetime
    education: list[str]
    experience: list[str]
    skills: list[str]
    projects: list[str]
    certifications: list[str]
    sections_found: list[str]
