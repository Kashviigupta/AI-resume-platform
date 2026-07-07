from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.db import Base


class Resume(Base):
    """
    A single uploaded resume file, plus its extracted text and parsed
    sections (stored as JSON text — SQLite has no native JSON column type).
    One resume can have many analyses (e.g. re-analyzed against different
    job descriptions over time).
    """

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)        # filled in during Milestone 7
    parsed_json = Column(Text, nullable=True)      # education/experience/skills/etc, filled in Milestone 7

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="resumes")
    analyses = relationship(
        "Analysis", back_populates="resume", cascade="all, delete-orphan"
    )
