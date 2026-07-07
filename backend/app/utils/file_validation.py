import os

from fastapi import UploadFile, HTTPException, status

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
PDF_MAGIC = b"%PDF"
DOCX_MAGIC = b"PK"  # .docx files are actually zip archives under the hood


def validate_resume_file(file: UploadFile, contents: bytes) -> None:
    """
    Raises an HTTPException (which FastAPI turns into a proper error response)
    if the uploaded file isn't a valid, appropriately-sized PDF or DOCX.
    Called with the file's raw bytes already read into memory.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf and .docx files are supported.",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    # "Magic bytes" check: confirms the file's actual content matches its extension,
    # so a renamed .txt-as-.pdf doesn't sneak through.
    if ext == ".pdf" and not contents.startswith(PDF_MAGIC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File does not look like a valid PDF.")
    if ext == ".docx" and not contents.startswith(DOCX_MAGIC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File does not look like a valid DOCX.")
