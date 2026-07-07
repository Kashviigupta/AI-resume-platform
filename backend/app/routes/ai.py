import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import resume_service, analysis_service
from app.services import ai_service
from app.schemas.ai import (
    RewriteBulletRequest,
    CoverLetterRequest,
    OptimizeATSRequest,
    ImproveResumeRequest,
)

router = APIRouter()


def _get_owned_resume(db: Session, resume_id: int, user: User):
    resume = resume_service.get_resume_by_id(db, resume_id, user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(
            status_code=422, detail="This resume has no extracted text — re-upload it first."
        )
    return resume


@router.post("/rewrite-bullet")
def rewrite_bullet(
    payload: RewriteBulletRequest,
    current_user: User = Depends(get_current_user),
):
    """Rewrites a single bullet point the user types in directly — no resume lookup needed."""
    result = ai_service.rewrite_bullet_point(payload.bullet_text)
    return result.model_dump()


@router.post("/summary/{resume_id}")
def resume_summary(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    resume = _get_owned_resume(db, resume_id, current_user)
    result = ai_service.generate_summary(resume.raw_text)
    return result.model_dump()


@router.post("/cover-letter/{resume_id}")
def cover_letter(
    resume_id: int,
    payload: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(db, resume_id, current_user)
    result = ai_service.generate_cover_letter(
        resume_text=resume.raw_text,
        job_description_text=payload.job_description_text,
        company_name=payload.company_name,
    )
    return result.model_dump()


@router.post("/optimize-ats/{resume_id}")
def optimize_ats(
    resume_id: int,
    payload: OptimizeATSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(db, resume_id, current_user)

    missing_skills = payload.missing_skills
    if missing_skills is None:
        # Fall back to the most recent Milestone 9 JD match saved for this resume.
        analyses = analysis_service.get_analyses_for_resume(db, resume.id)
        jd_analyses = [a for a in analyses if a.match_score is not None]
        if jd_analyses:
            data = json.loads(jd_analyses[0].missing_skills_json or "{}")
            missing_skills = data.get("missing_skills", [])
        else:
            missing_skills = []

    result = ai_service.optimize_for_ats(resume.raw_text, missing_skills)
    return result.model_dump()


@router.post("/improve-resume/{resume_id}")
def improve_resume(
    resume_id: int,
    payload: ImproveResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(db, resume_id, current_user)
    parsed = json.loads(resume.parsed_json) if resume.parsed_json else {}

    result = ai_service.improve_resume(
        resume_text=resume.raw_text,
        experience_bullets=parsed.get("experience", []),
        project_bullets=parsed.get("projects", []),
        job_description_text=payload.job_description_text,
    )
    return result.model_dump()
