import os

from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def extract_resume_text(file_path: str) -> str:
    """Dispatches to the right extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    raise ValueError(f"Unsupported file extension: {ext}")
