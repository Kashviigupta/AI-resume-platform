from datetime import datetime

from pydantic import BaseModel, Field


class JDMatchRequest(BaseModel):
    """Shape of the JSON body the frontend sends to POST /jd/match."""

    resume_id: int
    job_description_text: str = Field(min_length=20, description="Paste the full job description here.")


class JDMatchResponse(BaseModel):
    """Shape returned from POST /jd/match and GET /jd/history/{resume_id}."""

    analysis_id: int
    resume_id: int
    match_score: float
    jd_keywords: list[str]
    jd_skills_found: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime
