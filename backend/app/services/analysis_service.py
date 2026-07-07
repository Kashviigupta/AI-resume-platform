from sqlalchemy.orm import Session

from app.models.analysis import Analysis


def create_analysis(db: Session, resume_id: int, **scores_and_json) -> Analysis:
    """
    scores_and_json accepts any of: job_description_text, ats_score, quality_score,
    match_score, missing_skills_json, suggestions_json — whichever a given
    milestone's scoring step has computed so far.
    """
    analysis = Analysis(resume_id=resume_id, **scores_and_json)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analyses_for_resume(db: Session, resume_id: int) -> list[Analysis]:
    return (
        db.query(Analysis)
        .filter(Analysis.resume_id == resume_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


def get_all_analyses_for_user(db: Session, user_id: int) -> list[Analysis]:
    """Joins through Resume to scope analyses to a specific user — powers the dashboard history."""
    from app.models.resume import Resume  # local import avoids a circular import at module load time

    return (
        db.query(Analysis)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
