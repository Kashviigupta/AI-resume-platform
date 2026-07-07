from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.db import Base


class Analysis(Base):
    """
    One scoring run against a resume. `job_description_text` is nullable
    because a general "how good is my resume" analysis (Milestone 8) has no
    JD, while a match analysis (Milestone 9) does. We never overwrite a past
    analysis — a new row is created each time — so the dashboard (Milestone 11)
    can chart score history.
    """

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    job_description_text = Column(Text, nullable=True)

    ats_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    match_score = Column(Float, nullable=True)

    missing_skills_json = Column(Text, nullable=True)
    suggestions_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analyses")
