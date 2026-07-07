import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import resume_service, analysis_service
from app.services.scoring_service import compute_ats_score, compute_quality_score
from app.schemas.analysis import AnalysisOut, AnalysisHistoryOut

router = APIRouter()


def _overall(ats_score: float, quality_score: float) -> float:
    """ATS-friendliness matters slightly more than writing polish for getting past the bot stage."""
    return round(0.6 * (ats_score or 0) + 0.4 * (quality_score or 0), 1)


def _analysis_type(a) -> str:
    """A row has match_score set only if it came from the JD-match flow (Milestone 9);
    everything else came from the plain ATS-score flow (Milestone 8)."""
    return "jd_match" if a.match_score is not None else "ats"


@router.get("", response_model=list[AnalysisHistoryOut])
def list_all_analyses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Every analysis the current user has ever run, across every resume they've
    uploaded — most recent first. Powers the Dashboard's score-trend charts
    and the full History table (Milestone 11).
    """
    analyses = analysis_service.get_all_analyses_for_user(db, current_user.id)

    result = []
    for a in analyses:
        overall = (
            _overall(a.ats_score, a.quality_score)
            if a.ats_score is not None and a.quality_score is not None
            else None
        )
        result.append(
            AnalysisHistoryOut(
                id=a.id,
                resume_id=a.resume_id,
                resume_filename=a.resume.filename,
                analysis_type=_analysis_type(a),
                ats_score=a.ats_score,
                quality_score=a.quality_score,
                match_score=a.match_score,
                overall_score=overall,
                created_at=a.created_at,
            )
        )
    return result


@router.post("/{resume_id}/ats-score", response_model=AnalysisOut)
def analyze_resume(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    resume = resume_service.get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(status_code=422, detail="This resume has no extracted text to analyze.")

    parsed = json.loads(resume.parsed_json) if resume.parsed_json else {}

    ats_score, ats_reasons = compute_ats_score(resume.raw_text, parsed)
    quality_score, quality_suggestions = compute_quality_score(resume.raw_text)

    analysis = analysis_service.create_analysis(
        db,
        resume_id=resume.id,
        ats_score=ats_score,
        quality_score=quality_score,
        suggestions_json=json.dumps(
            {"ats_reasons": ats_reasons, "quality_suggestions": quality_suggestions}
        ),
    )

    return AnalysisOut(
        id=analysis.id,
        resume_id=resume.id,
        ats_score=ats_score,
        quality_score=quality_score,
        overall_score=_overall(ats_score, quality_score),
        ats_reasons=ats_reasons,
        quality_suggestions=quality_suggestions,
        created_at=analysis.created_at,
    )


@router.get("/{resume_id}", response_model=list[AnalysisOut])
def list_analyses(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Every past analysis for this resume, most recent first — powers score-history charts later."""
    resume = resume_service.get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    analyses = analysis_service.get_analyses_for_resume(db, resume_id)
    result = []
    for a in analyses:
        data = json.loads(a.suggestions_json) if a.suggestions_json else {}
        result.append(
            AnalysisOut(
                id=a.id,
                resume_id=a.resume_id,
                ats_score=a.ats_score,
                quality_score=a.quality_score,
                overall_score=_overall(a.ats_score, a.quality_score),
                ats_reasons=data.get("ats_reasons", []),
                quality_suggestions=data.get("quality_suggestions", []),
                created_at=a.created_at,
            )
        )
    return result
