from pydantic import BaseModel, Field


class RewriteBulletRequest(BaseModel):
    """Body for POST /ai/rewrite-bullet — a single ad-hoc bullet, not tied to a saved resume."""

    bullet_text: str = Field(min_length=3)


class OptimizeATSRequest(BaseModel):
    """
    Body for POST /ai/optimize-ats/{resume_id}. missing_skills is optional —
    if omitted, the route falls back to the most recent Milestone 9 JD match
    saved for this resume.
    """

    missing_skills: list[str] | None = None


class ImproveResumeRequest(BaseModel):
    """Body for POST /ai/improve-resume/{resume_id}. job_description_text is optional."""

    job_description_text: str = ""


class CoverLetterRequest(BaseModel):
    """Body for POST /ai/cover-letter/{resume_id}."""

    job_description_text: str = Field(min_length=20)
    company_name: str = ""
