from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    """
    A registered account. One user can own many resumes (each resume they
    upload belongs to exactly one user).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # never store plain-text passwords
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship(
        "Resume", back_populates="owner", cascade="all, delete-orphan"
    )
