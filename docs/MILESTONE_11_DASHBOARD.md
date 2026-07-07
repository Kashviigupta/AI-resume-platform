# Milestone 11 — Analytics Dashboard

## What this milestone adds

Every previous milestone was already quietly writing the data this milestone
reads: every `POST /analysis/{id}/ats-score` and every `POST /jd/match` call
creates a new row in the `analyses` table instead of overwriting the last one
(see the docstring on the `Analysis` model). That means the score *history*
already existed in the database — Milestone 11 is almost entirely about
exposing it.

### Backend: one new endpoint

`GET /analysis` — returns every analysis for the logged-in user, across every
resume they've uploaded, most recent first. Each row is "flattened" so the
frontend gets everything it needs without extra requests:

```json
[
  {
    "id": 14,
    "resume_id": 3,
    "resume_filename": "resume_v2.pdf",
    "analysis_type": "jd_match",
    "ats_score": null,
    "quality_score": null,
    "match_score": 78.0,
    "overall_score": null,
    "created_at": "2026-07-02T09:14:00"
  },
  {
    "id": 13,
    "resume_id": 3,
    "resume_filename": "resume_v2.pdf",
    "analysis_type": "ats",
    "ats_score": 82.0,
    "quality_score": 74.0,
    "match_score": null,
    "overall_score": 78.8,
    "created_at": "2026-07-01T18:02:00"
  }
]
```

Notice `analysis_type` is computed on the backend (`"jd_match"` if
`match_score` is set, `"ats"` otherwise) — a beginner-friendly choice that
keeps that little bit of business logic in one place instead of duplicating
an `if` check in every frontend component that touches this list.

This single endpoint powers **both** new frontend features below — no
per-resume looping needed.

### Frontend: two new pages' worth of content

**Dashboard Home** (`/dashboard`) now shows:
- 4 stat cards: latest ATS score, latest quality score, latest match score,
  total resumes uploaded.
- Two line charts (via `react-chartjs-2`, already installed since Milestone
  2): ATS/quality score history, and job-match score history. Each chart
  shows a friendly empty state instead of a blank box when there's no data
  yet.
- A "Recent resumes" card grid (up to 6), linking back to Upload Resume.

**History** (`/dashboard/history`) now shows:
- A full, searchable (by filename) and filterable (All / ATS Analysis / JD
  Match) table of every analysis ever run, with all scores and the exact
  date/time.

### New reusable components

- `ScoreTrendChart.jsx` — wraps `react-chartjs-2`'s `<Line>` chart with the
  app's color palette and a 0–100 y-axis, since every score in this app is
  already normalized to that range.
- `ResumeCard.jsx` — a small summary card for one resume, used in the
  Dashboard's recent-resumes grid.

## Files changed in this milestone

```
backend/app/schemas/analysis.py     (added AnalysisHistoryOut)
backend/app/routes/analysis.py      (added GET /analysis)
frontend/src/services/analysisService.js  (added listAllAnalyses)
frontend/src/components/ScoreTrendChart.jsx  (new)
frontend/src/components/ResumeCard.jsx       (new)
frontend/src/pages/DashboardHome.jsx  (rewritten — was a placeholder)
frontend/src/pages/History.jsx        (rewritten — was a placeholder)
```

No new packages are required — `chart.js` and `react-chartjs-2` were already
in `package.json` from Milestone 2, anticipating this milestone.

## How to test it

1. Make sure the backend is running (`uvicorn app.main:app --reload` from
   `backend/`) and the frontend is running (`npm run dev` from `frontend/`).
2. Log in, upload 2–3 resumes from **Upload Resume**, and click **Run ATS
   Analysis** on each one.
3. Go to **Job Match**, paste a job description, and match it against one of
   your resumes a couple of times (with slightly different pasted text is
   fine — it's just to generate a few data points).
4. Go to **Dashboard** (the Overview link) — you should see the stat cards
   populated and both charts showing lines with real points.
5. Go to **History** — you should see every analysis you just ran, in a
   table. Try the search box and the filter buttons.

## Common errors and fixes

| Symptom | Fix |
|---|---|
| Charts show "Not enough data yet" even after running an analysis | Hard-refresh the Dashboard page — it only fetches on mount, so it won't auto-update while you're still on the Upload page in another action. |
| `GET /analysis` returns `401 Unauthorized` | Your JWT token expired (1 day by default) — log out and back in. |
| Charts render at 0 height / invisible | Make sure `chart.js` and `react-chartjs-2` installed correctly — re-run `npm install` inside `frontend/`. |
| History table's Type badges are all "ATS Analysis" | You haven't run any JD Match yet — that's expected; go run one from the Job Match page. |
