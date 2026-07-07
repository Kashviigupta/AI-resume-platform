# AI Resume Improvement Platform — Milestone 1: Project Planning

## 1. Problem Statement

Most students and early-career job seekers write resumes without knowing:
- Whether their resume will even pass an Applicant Tracking System (ATS) before a human sees it
- How well their resume matches a specific job description
- Which skills they're missing for a target role
- Whether their bullet points sound impactful or weak ("responsible for..." vs "led...")

Professional resume review services are expensive and slow. This platform gives users instant,
AI-powered, data-backed feedback — for free — using their own uploaded resume and a job description
of their choice.

## 2. Objectives

1. Let a user register, log in, and securely manage their own resumes.
2. Extract and parse structured data (education, experience, skills, projects, certifications) from
   an uploaded PDF/DOCX resume.
3. Score the resume for ATS-friendliness and general quality.
4. Compare the resume against a job description and produce a match score + missing skills list.
5. Use Gemini to generate concrete rewrite suggestions (bullet points, summary, cover letter).
6. Store every analysis so the user can track improvement over time on a dashboard.

## 3. Core Features (from your spec)

| # | Feature | Milestone |
|---|---------|-----------|
| 1 | Register / Login (JWT) | 5 |
| 2 | Upload Resume (PDF/DOCX) | 6 |
| 3 | Resume Text Extraction | 7 |
| 4 | Resume Section Parsing | 7 |
| 5 | ATS Score | 8 |
| 6 | Resume Quality Analysis | 8 |
| 7 | JD Comparison + Match Score | 9 |
| 8 | Missing Skills Extraction | 9 |
| 9 | AI Rewrite Suggestions (Gemini) | 10 |
| 10 | Resume Summary / Cover Letter Generation | 10 |
| 11 | Resume History | 11 |
| 12 | Analytics Dashboard | 11 |
| 13 | Download Improved Resume | 10/11 |

## 4. User Stories

- **As a new user**, I want to register with email + password so I can save my resume history.
- **As a returning user**, I want to log in and see all my past resume analyses.
- **As a job seeker**, I want to upload my resume and instantly see an ATS score with reasons.
- **As a job seeker**, I want to paste a job description and see how well my resume matches it.
- **As a job seeker**, I want AI-rewritten bullet points so I don't have to guess how to phrase things.
- **As a job seeker**, I want a generated cover letter tailored to the job description.
- **As a returning user**, I want a dashboard showing how my scores have improved across resume versions.

## 5. Software Architecture

```
                    ┌─────────────────────────┐
                    │        Browser           │
                    │  React (Vite) + Tailwind │
                    └────────────┬──────────────┘
                                 │  Axios (REST, JWT in header)
                                 ▼
                    ┌─────────────────────────┐
                    │        FastAPI            │
                    │  routes/ (auth, resume,   │
                    │  analysis, jd, ai, history)│
                    └──────┬───────────┬─────────┘
                           │           │
              ┌────────────┘           └─────────────┐
              ▼                                       ▼
   ┌─────────────────────┐               ┌───────────────────────┐
   │   SQLite (SQLAlchemy) │               │  AI / NLP services      │
   │  users, resumes,      │               │  spaCy, NLTK,           │
   │  analyses, jd_matches │               │  sentence-transformers, │
   └─────────────────────┘               │  scikit-learn, Gemini   │
                                          └───────────────────────┘
```

One FastAPI backend, one React frontend, one SQLite file. No microservices, no queues — everything
runs synchronously in-process, which is appropriate at this scale and keeps deployment simple (Render
free tier + Vercel free tier).

## 6. Folder Structure

### Frontend
```
frontend/src/
  components/   -> reusable UI pieces (Navbar, Sidebar, ScoreCard, Charts, ProtectedRoute)
  pages/         -> one file per route (Landing, Login, Register, Dashboard, UploadResume, ...)
  hooks/         -> reusable stateful logic (useAuth, useResumeHistory)
  services/      -> axios instance + API call functions, one file per backend resource
  assets/        -> images/icons
  utils/         -> formatters, constants, validators
```
Why this split: pages own layout + data-fetching; components are dumb/reusable; services isolate all
network code so pages never call axios directly (easy to mock/test); hooks hold cross-page state logic
like "am I logged in."

### Backend
```
backend/app/
  routes/       -> FastAPI routers, one file per resource (auth.py, resumes.py, analysis.py, jd.py, ai.py)
  models/       -> SQLAlchemy ORM table definitions
  schemas/      -> Pydantic request/response models (kept separate from ORM models on purpose)
  services/     -> business logic: parsing, scoring, matching, gemini calls (routes stay thin)
  database/     -> engine/session setup, init logic
  auth/         -> password hashing, JWT creation/verification, current-user dependency
  utils/        -> file handling, text cleaning helpers
```
Why this split: this is the standard FastAPI layered architecture — routes only handle HTTP concerns,
services hold logic, models/schemas are separated so your database shape can evolve independently of
your API's public shape.

## 7. Database Design

```
users
 ├─ id (PK)
 ├─ full_name
 ├─ email (unique)
 ├─ hashed_password
 └─ created_at

resumes                              (one user -> many resumes)
 ├─ id (PK)
 ├─ user_id (FK -> users.id)
 ├─ filename
 ├─ file_path
 ├─ raw_text
 ├─ parsed_json      (education/experience/skills/projects/certs as JSON text)
 └─ uploaded_at

analyses                             (one resume -> many analyses, since JD changes each time)
 ├─ id (PK)
 ├─ resume_id (FK -> resumes.id)
 ├─ job_description_text  (nullable — null if it's a general quality analysis)
 ├─ ats_score
 ├─ quality_score
 ├─ match_score            (nullable)
 ├─ missing_skills_json    (nullable)
 ├─ suggestions_json
 └─ created_at
```
Relationships: `User 1—* Resume`, `Resume 1—* Analysis`. Storing every analysis (not overwriting)
is what powers the "track improvement over time" dashboard requirement.

## 8. API Design (high-level; full endpoint code arrives per-milestone)

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | /auth/register | No | Create account |
| POST | /auth/login | No | Get JWT |
| GET  | /auth/me | Yes | Current user info |
| GET  | /health | No | Health check |
| POST | /resumes/upload | Yes | Upload + parse resume |
| GET  | /resumes | Yes | List user's resumes |
| GET  | /resumes/{id} | Yes | Get one resume detail |
| POST | /analysis/{resume_id}/ats-score | Yes | Compute ATS + quality score |
| POST | /analysis/{resume_id}/match | Yes | Compare against a JD, get match score |
| POST | /ai/rewrite-bullet | Yes | Gemini: rewrite a bullet point |
| POST | /ai/summary | Yes | Gemini: generate resume summary |
| POST | /ai/cover-letter | Yes | Gemini: generate cover letter |
| GET  | /history | Yes | All past analyses for dashboard |

## 9. UI Wireframes (ASCII)

**Landing Page**
```
┌──────────────────────────────────────────────┐
│ Logo        Features  Pricing   [Login][Sign] │
├──────────────────────────────────────────────┤
│         Get your resume past the bots.        │
│      Upload. Analyze. Improve. Get hired.      │
│              [ Get Started → ]                │
└──────────────────────────────────────────────┘
```

**Dashboard (post-login)**
```
┌───────┬──────────────────────────────────────┐
│ Side  │  Welcome back, Kashvi                 │
│ bar   │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│       │  │ATS: 78  │ │Match:64 │ │Resumes:3│  │
│ Home  │  └─────────┘ └─────────┘ └─────────┘  │
│ Upload│  ─────────── Score over time chart ── │
│ History│  Recent resumes:                     │
│ Settings│  [resume_v2.pdf  ATS 78  view→]      │
└───────┴──────────────────────────────────────┘
```

This document is the reference point for every milestone that follows — file structure and naming
in the actual code matches exactly what's laid out here.
