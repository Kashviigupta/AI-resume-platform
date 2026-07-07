from datetime import datetime

from pydantic import BaseModel


class AnalysisOut(BaseModel):
    """Shape returned from POST /analysis/{resume_id}/ats-score and GET /analysis/{resume_id}."""

    id: int
    resume_id: int
    ats_score: float
    quality_score: float
    overall_score: float
    ats_reasons: list[str]
    quality_suggestions: list[str]
    created_at: datetime


class AnalysisHistoryOut(BaseModel):
    """
    Shape returned from GET /analysis — every analysis the current user has
    ever run, across every resume, most recent first. This single flat list
    is what powers both the Dashboard's score-trend charts and the History
    page's table (Milestone 11), so the frontend never has to loop over
    resumes and call a per-resume endpoint one at a time.
    """

    id: int
    resume_id: int
    resume_filename: str
    analysis_type: str  # "ats" or "jd_match" — computed on the backend so the
    # frontend never has to guess which fields will be populated.
    ats_score: float | None
    quality_score: float | None
    match_score: float | None
    overall_score: float | None
    created_at: datetime
