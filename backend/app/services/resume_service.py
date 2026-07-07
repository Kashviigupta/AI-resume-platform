from sqlalchemy.orm import Session

from app.models.resume import Resume


def create_resume(db: Session, user_id: int, filename: str, file_path: str) -> Resume:
    resume = Resume(user_id=user_id, filename=filename, file_path=file_path)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resumes_for_user(db: Session, user_id: int) -> list[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )


def get_resume_by_id(db: Session, resume_id: int, user_id: int) -> Resume | None:
    """Scoped to user_id too, so one user can never fetch another user's resume by guessing an id."""
    return (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == user_id)
        .first()
    )


def delete_resume(db: Session, resume_id: int, user_id: int) -> bool:
    resume = get_resume_by_id(db, resume_id, user_id)
    if not resume:
        return False
    db.delete(resume)
    db.commit()
    return True
