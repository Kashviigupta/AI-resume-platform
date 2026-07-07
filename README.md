# AI Resume Improvement Platform — Milestones 1–12 (Complete)

A full-stack web app where users register, upload a resume (PDF/DOCX), get it
parsed into sections, scored for ATS-friendliness and writing quality,
matched against a pasted job description, improved with Gemini AI (rewritten
bullets, summaries, cover letters), and can track all of that history on an
analytics dashboard — deployed live on Vercel + Render.

This package contains the **entire project, all 12 milestones merged
together** — not a diff. Every file needed to run the app locally or deploy
it is here.

## What's included, by milestone

| Milestone | What it added |
|---|---|
| 1 — Planning | `docs/MILESTONE_1_PLANNING.md`: problem statement, architecture, DB design, API design, wireframes |
| 2 — Frontend setup | Vite + React + Tailwind, routing, Navbar/Sidebar, Landing/Login/Register pages, protected Dashboard layout |
| 3 — Backend setup | FastAPI app, config via env vars, SQLite connection, `/health` check |
| 4 — Database | `User`/`Resume`/`Analysis` SQLAlchemy models, relationships, CRUD helpers |
| 5 — Authentication | Register/Login APIs, bcrypt password hashing, JWT auth, protected routes, persistent frontend login |
| 6 — Resume upload | Upload UI, PDF/DOCX validation, file storage on disk |
| 7 — Resume parsing | Text extraction + section parsing (education/experience/skills/projects/certifications) |
| 8 — Resume analysis | ATS score, writing-quality score (weak verbs, passive voice, etc.), itemized human-readable suggestions |
| 9 — JD matching | Paste a job description, get a match score, matched vs. missing skills (cosine similarity over keywords) |
| 10 — Gemini AI integration | Rewrite bullets, improve projects/experience, generate summary, generate cover letter — structured JSON via Gemini |
| 11 — Dashboard | Real analytics: stat cards, ATS/quality/match score-trend charts, recent-resumes grid, full searchable/filterable History table |
| 12 — Deployment | `render.yaml` (backend → Render) + `vercel.json` (frontend → Vercel), full deployment guide |

Nothing here is a mockup — every milestone was built, tested end-to-end in a
sandbox, then packaged.

## Project structure

```
ai-resume-platform/
├── frontend/                  React (Vite) + Tailwind
│   ├── src/
│   │   ├── components/        Navbar, Sidebar, DashboardLayout, ProtectedRoute,
│   │   │                      ScoreBar, ScoreTrendChart, ResumeCard
│   │   ├── pages/              Landing, Login, Register, DashboardHome, UploadResume,
│   │   │                      JDMatch, AITools, History, Settings
│   │   ├── hooks/              useAuth (auth context + persistent session)
│   │   └── services/           api.js (axios instance) + one file per API area
│   └── vercel.json            Deployment config (Milestone 12)
├── backend/                    FastAPI
│   ├── app/
│   │   ├── auth/               JWT + password hashing
│   │   ├── database/            SQLAlchemy engine/session
│   │   ├── models/              User, Resume, Analysis
│   │   ├── schemas/             Pydantic request/response shapes
│   │   ├── routes/              health, auth, resumes, analysis, jd, ai
│   │   ├── services/            business logic per domain
│   │   └── utils/               file validation, text extraction
│   └── render.yaml             Deployment config (Milestone 12)
└── docs/                        One planning/reference doc per major milestone
```

## Running it locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste in your real GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for the interactive API explorer and
`http://localhost:8000/health` to confirm it's alive.

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Visit `http://localhost:5173`.

## Deploying it live

See `docs/MILESTONE_12_DEPLOYMENT.md` for the full step-by-step guide
(Render for the backend, Vercel for the frontend, environment variable
reference, and what SQLite's ephemeral-filesystem tradeoff means on a free
tier).

## Common errors & fixes

- **`ModuleNotFoundError` on backend start** → activate the venv and run `pip install -r requirements.txt`.
- **Frontend shows a CORS error in console** → backend `.env`'s `FRONTEND_ORIGIN` must exactly match the frontend's origin (no trailing slash), and the backend must be restarted after editing `.env`.
- **Login "Network Error" in browser** → backend isn't running, or `frontend/.env`'s `VITE_API_URL` doesn't point to it.
- **`sqlite3.OperationalError: no such table`** → happens if you delete `resume_platform.db` without restarting the backend (the startup event recreates tables).
- **Registering gives a 500 error mentioning `bcrypt`** → run `pip install bcrypt==4.0.1` (newer bcrypt breaks passlib 1.7.4).
- **"No text could be extracted from this file"** → the PDF is a scanned image, not selectable text. Export directly from Word/Google Docs instead.
- **A resume section shows "Not detected"** → the parser looks for common headers like "Experience"/"Skills"/"Education"; unusual header wording won't match yet — extend `SECTION_HEADERS` in `app/services/resume_parser.py`.
- **Gemini calls fail (AI Tools page)** → check `GEMINI_API_KEY` is set correctly in `backend/.env` (or on Render, set manually since it's marked `sync: false`).
- **Dashboard/History show no data** → run at least one ATS analysis (Upload Resume page) or JD match (Job Match page) first — the charts/table only show analyses that have actually been run.
- **Deployed app: data disappears after a while** → expected on Render's free tier (ephemeral filesystem) — see `docs/MILESTONE_12_DEPLOYMENT.md` section 8 for the paid persistent-disk upgrade path.

## Docs

- `docs/MILESTONE_1_PLANNING.md` — original planning doc (architecture, DB/API design, wireframes)
- `docs/MILESTONE_11_DASHBOARD.md` — analytics dashboard design + testing notes
- `docs/MILESTONE_12_DEPLOYMENT.md` — full deployment guide
