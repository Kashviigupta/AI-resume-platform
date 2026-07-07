from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import init_db
from app.routes import health, auth, resumes, analysis, jd, ai
import app.models  # noqa: F401 — importing registers all tables on Base.metadata before init_db() runs

app = FastAPI(title=settings.APP_NAME)

# Allow the React frontend (running on a different origin/port during dev)
# to call this API. In production, set FRONTEND_ORIGIN to your deployed
# Vercel URL via an environment variable.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(jd.router, prefix="/jd", tags=["job-description"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


@app.get("/")
def root():
    return {"message": "AI Resume Improvement Platform API is running. See /docs for the API explorer."}
