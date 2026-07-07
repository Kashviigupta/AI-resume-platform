# Importing every model here means "import app.models" (done once in main.py)
# registers all tables on Base.metadata, so init_db() creates them all.
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis

__all__ = ["User", "Resume", "Analysis"]
