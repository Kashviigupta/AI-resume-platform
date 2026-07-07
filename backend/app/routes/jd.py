import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import resume_service, analysis_service
from app.services.jd_service import analyze_job_description
from app.schemas.jd import JDMatchRequest, JDMatchResponse

router = APIRouter()


def _to_response(analysis) -> JDMatchResponse:
    missing = json.loads(analysis.missing_skills_json) if analysis.missing_skills_json else {}
    return JDMatchResponse(
        analysis_id=analysis.id,
        resume_id=analysis.resume_id,
        match_score=analysis.match_score or 0.0,
        jd_keywords=missing.get("jd_keywords", []),
        jd_skills_found=missing.get("jd_skills_found", []),
        matched_skills=missing.get("matched_skills", []),
        missing_skills=missing.get("missing_skills", []),
        created_at=analysis.created_at,
    )


@router.post("/match", response_model=JDMatchResponse, status_code=201)
def match_job_description(
    payload: JDMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compares one resume against a pasted job description and saves the result
    as a new Analysis row (so History/Dashboard can show match-score trends
    over time, same as the Milestone 8 ATS analyses).
    """
    resume = resume_service.get_resume_by_id(db, payload.resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(
            status_code=422, detail="This resume has no extracted text — re-upload it first."
        )

    parsed = json.loads(resume.parsed_json) if resume.parsed_json else {}
    resume_skills = parsed.get("skills", [])

    result = analyze_job_description(
        resume_text=resume.raw_text,
        resume_skills=resume_skills,
        jd_text=payload.job_description_text,
    )

    analysis = analysis_service.create_analysis(
        db,
        resume_id=resume.id,
        job_description_text=payload.job_description_text,
        match_score=result["match_score"],
        missing_skills_json=json.dumps(result),
    )

    return _to_response(analysis)


@router.get("/history/{resume_id}", response_model=list[JDMatchResponse])
def jd_match_history(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Every past JD match for this resume (analyses that have a match_score), most recent first."""
    resume = resume_service.get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    analyses = analysis_service.get_analyses_for_resume(db, resume_id)
    jd_analyses = [a for a in analyses if a.match_score is not None]
    return [_to_response(a) for a in jd_analyses]
