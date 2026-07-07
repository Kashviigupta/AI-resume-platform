import json
import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.config import settings
from app.utils.file_validation import validate_resume_file
from app.utils.text_extraction import extract_resume_text
from app.services.resume_parser import parse_resume_sections, sections_to_json
from app.services import resume_service
from app.schemas.resume import ResumeOut, ResumeDetail

router = APIRouter()


@router.post("/upload", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full Milestone 6+7 flow in one request: validate -> save to disk ->
    extract text -> parse sections -> store everything on the Resume row.
    """
    contents = await file.read()
    validate_resume_file(file, contents)

    # Save under uploaded_resumes/<user_id>/<random-name>.<ext> — the random
    # name avoids collisions if two people upload a file called "resume.pdf".
    user_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(user_dir, stored_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        raw_text = extract_resume_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read text from this file: {e}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this file — it may be a scanned image rather than selectable text.",
        )

    parsed = parse_resume_sections(raw_text)

    resume = resume_service.create_resume(
        db, user_id=current_user.id, filename=file.filename, file_path=file_path
    )
    resume.raw_text = raw_text
    resume.parsed_json = sections_to_json(parsed)
    db.commit()
    db.refresh(resume)

    return ResumeDetail(id=resume.id, filename=resume.filename, uploaded_at=resume.uploaded_at, **parsed)


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return resume_service.get_resumes_for_user(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    resume = resume_service.get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    parsed = json.loads(resume.parsed_json) if resume.parsed_json else {}
    return ResumeDetail(
        id=resume.id,
        filename=resume.filename,
        uploaded_at=resume.uploaded_at,
        education=parsed.get("education", []),
        experience=parsed.get("experience", []),
        skills=parsed.get("skills", []),
        projects=parsed.get("projects", []),
        certifications=parsed.get("certifications", []),
        sections_found=parsed.get("sections_found", []),
    )
