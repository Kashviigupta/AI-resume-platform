# Milestone 12 — Deployment

Goal: get the AI Resume Improvement Platform live on the public internet,
using only free-tier services, matching the stack decided back in Milestone
1 — **Vercel** for the React frontend, **Render** for the FastAPI backend,
SQLite for the database (no separate database service to pay for).

---

## 1. Folder structure (what's new)

```
ai-resume-platform/
├── backend/
│   ├── render.yaml          <- NEW: Render Blueprint (one-click deploy config)
│   └── ... (unchanged)
├── frontend/
│   ├── vercel.json          <- NEW: SPA routing config for Vercel
│   └── ... (unchanged)
└── docs/
    └── MILESTONE_12_DEPLOYMENT.md   <- this file
```

Nothing else moves. Deployment configuration lives alongside the code it
deploys, which is why `render.yaml` is inside `backend/` and `vercel.json` is
inside `frontend/` rather than at the repo root.

## 2. Files created in this milestone

| File | Purpose |
|---|---|
| `backend/render.yaml` | Render "Blueprint" — describes your web service so Render can build+deploy it automatically from git, instead of you clicking through a setup form |
| `frontend/vercel.json` | Tells Vercel to serve `index.html` for every route, so refreshing `/dashboard/history` doesn't 404 (React Router handles routing client-side, so the server needs to always hand back the same HTML shell) |

---

## 3. Prerequisites

- A GitHub account, with this project pushed to a GitHub repo (both
  `backend/` and `frontend/` folders committed — **never commit your `.env`
  files**, only `.env.example`).
- A free [Render](https://render.com) account (sign up with GitHub — no
  credit card needed for the free tier).
- A free [Vercel](https://vercel.com) account (sign up with GitHub).
- Your Gemini API key from Milestone 10, ready to paste in as a secret.

If you haven't pushed to GitHub yet:
```bash
cd ai-resume-platform
git init
git add .
git commit -m "AI Resume Improvement Platform — milestones 1-12"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-resume-platform.git
git push -u origin main
```

---

## 4. Deploy the backend to Render

1. Go to <https://dashboard.render.com> → **New +** → **Blueprint**.
2. Connect your GitHub account if you haven't already, and select your
   `ai-resume-platform` repo.
3. Render detects `backend/render.yaml` automatically (because of `rootDir:
   backend` inside it) and shows you a preview of the service it's about to
   create — a free web service named `ai-resume-platform-api`.
4. Before clicking **Apply**, you'll be prompted for the env vars marked
   `sync: false` in `render.yaml` — paste in your real `GEMINI_API_KEY` here.
   (`JWT_SECRET_KEY` is generated for you automatically — you don't need to
   type anything for it.)
5. Click **Apply**. Render will build (`pip install -r requirements.txt`)
   and start (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`) your
   service. First build takes a few minutes since it's installing spaCy,
   sentence-transformers, and scikit-learn.
6. Once live, Render gives you a URL like
   `https://ai-resume-platform-api.onrender.com`. Visit
   `https://ai-resume-platform-api.onrender.com/health` — you should see
   `{"status": "ok"}` (or whatever your Milestone 3 health check returns).
   Visit `/docs` to confirm the interactive API explorer loads.

**Don't have a `render.yaml` / prefer the manual dashboard route?** Click
**New +** → **Web Service** instead, point it at your repo, set **Root
Directory** to `backend`, **Build Command** to `pip install -r
requirements.txt`, **Start Command** to `uvicorn app.main:app --host 0.0.0.0
--port $PORT`, then add the same environment variables listed in
`render.yaml` manually under the service's **Environment** tab.

---

## 5. Deploy the frontend to Vercel

1. First, point the frontend at your live backend URL. Locally, create
   `frontend/.env.production`:
   ```
   VITE_API_URL=https://ai-resume-platform-api.onrender.com
   ```
   Commit this file (it contains no secrets — it's just a public URL, same
   idea as `FRONTEND_ORIGIN` on the backend side).

2. Go to <https://vercel.com/new>, import the same GitHub repo.
3. Vercel asks for a **Root Directory** — set it to `frontend`.
4. Framework Preset should auto-detect as **Vite**. Leave Build Command
   (`npm run build`) and Output Directory (`dist`) as Vercel's defaults —
   `vercel.json` already matches these, so nothing extra to configure.
5. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://ai-resume-platform-api.onrender.com` |
6. Click **Deploy**. Vercel gives you a URL like
   `https://ai-resume-platform.vercel.app`.

## 6. Close the loop: update CORS on the backend

Right now the backend's `FRONTEND_ORIGIN` env var is still set to the
placeholder from `render.yaml`. Go back to your Render service → **Environment**
tab → update `FRONTEND_ORIGIN` to your real Vercel URL:
```
FRONTEND_ORIGIN=https://ai-resume-platform.vercel.app
```
Save — Render automatically redeploys with the new value. Without this step,
your deployed frontend's API calls will be blocked by the browser with a CORS
error, even though the backend itself is running fine.

---

## 7. Environment variables — full reference

**Backend (Render → Environment tab):**
| Variable | Example value | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./resume_platform.db` | See disk note below |
| `JWT_SECRET_KEY` | *(auto-generated)* | Never reuse your local dev value in production |
| `JWT_ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | |
| `FRONTEND_ORIGIN` | `https://ai-resume-platform.vercel.app` | Must match your Vercel URL exactly, no trailing slash |
| `GEMINI_API_KEY` | *(your real key)* | Set manually — marked `sync: false` |
| `GEMINI_MODEL` | `gemini-2.5-flash` | |
| `UPLOAD_DIR` | `uploaded_resumes` | See disk note below |
| `MAX_UPLOAD_SIZE_MB` | `5` | |

**Frontend (Vercel → Environment Variables):**
| Variable | Example value |
|---|---|
| `VITE_API_URL` | `https://ai-resume-platform-api.onrender.com` |

---

## 8. Deploying the database (the SQLite reality check)

This project deliberately uses SQLite (per the Milestone 1 tech stack — no
Postgres, no separate DB service to configure or pay for). That has one
real consequence in production worth understanding, not glossing over:

> **Render's Free web services have an ephemeral filesystem.** Every time
> the service redeploys (e.g. you push new code) or restarts (e.g. it spins
> down after 15 minutes of inactivity and wakes back up), any files it wrote
> locally — including `resume_platform.db` and everything in
> `uploaded_resumes/` — are wiped and it starts fresh.

For a student project / portfolio demo, this is usually fine: you can
register a fresh account each time you want to show it off, or accept that
data doesn't need to survive forever. But it's worth knowing so a "vanished"
account after a few hours of no traffic doesn't look like a bug.

If you need real persistence (e.g. showing this to recruiters over several
days without re-registering):
1. Upgrade the Render service from `plan: free` to `plan: starter`
   ($7/month) in `render.yaml` (or in the dashboard).
2. Attach a **Persistent Disk** (an extra ~$0.25/GB/month) mounted at, say,
   `/var/data` — the commented-out block at the bottom of `render.yaml`
   shows exactly what to uncomment.
3. Point `DATABASE_URL` and `UPLOAD_DIR` at paths inside that mount, e.g.
   `sqlite:////var/data/resume_platform.db` (note: four slashes — three for
   the `sqlite://` scheme plus one for the absolute path) and
   `/var/data/uploaded_resumes`.

This is intentionally left as an optional upgrade rather than the default,
since Milestone 1 specifically called for a little-to-no-budget stack.

---

## 9. Testing your deployment

1. Visit your Vercel URL. You should land on the Landing page.
2. Register a new account — confirm you land on `/dashboard` afterward.
3. Upload a resume (PDF or DOCX) and run an ATS analysis — confirm scores
   come back (this round-trips through Render, so it also proves CORS and
   JWT auth are both working end-to-end).
4. Go to **Job Match**, paste a job description, confirm a match score comes
   back (this is the step most likely to be slow on Render's free tier the
   *first* time, due to cold-start spin-up — give it up to a minute).
5. Go to **AI Tools**, try "Generate Summary" — confirms your `GEMINI_API_KEY`
   made it through correctly.
6. Go to **Dashboard** and **History** — confirms the Milestone 11 charts
   and table are reading real data through the deployed API.
7. Refresh the browser while on `/dashboard/history` directly (not just
   navigating there via clicks) — confirms `vercel.json`'s rewrite rule is
   working and you don't get a 404.

## 10. Common errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Frontend loads but every API call fails with a CORS error in the browser console | `FRONTEND_ORIGIN` on Render doesn't match your Vercel URL exactly | Update the env var on Render (Section 6), including protocol (`https://`) and no trailing slash |
| First request after a while takes ~30–60 seconds | Render Free web services spin down after 15 minutes of inactivity | Expected behavior on the free tier; upgrade to a paid plan to remove it |
| Refreshing `/dashboard/*` routes shows a Vercel 404 page | `vercel.json` missing or Root Directory wasn't set to `frontend` | Confirm `vercel.json` is committed inside `frontend/` and redeploy |
| Data (resumes, accounts) disappears after a day or two | Free Render web services have an ephemeral filesystem | Expected on free tier — see Section 8 for the paid persistent-disk upgrade |
| Gemini calls (AI Tools page) fail with an auth error | `GEMINI_API_KEY` wasn't set, or was set with `sync: true` and got wiped | Re-set it manually under Render → Environment tab |
| Build fails on Render installing `sentence-transformers` | Free tier's 512 MB RAM can be tight for the build step | Retry the deploy (transient), or trim unused ML packages if you're not using semantic-similarity matching yet |
| Backend `/health` works but `/docs` 404s | You're hitting the Vercel frontend URL instead of the Render backend URL | Double-check you're visiting the `.onrender.com` URL for API routes |
