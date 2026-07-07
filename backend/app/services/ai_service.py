"""
Wraps Google's Gemini API for every AI-generation feature in the app.

Why structured (JSON) output instead of free-form text: every one of these
functions feeds a specific UI element (a list of bullets, a single string,
etc). If we asked Gemini for free-form text and tried to regex/split it
ourselves, small wording changes in the model's response would break the
frontend. Instead we hand Gemini a Pydantic schema via `response_schema` and
it is contractually guaranteed to return JSON matching that shape — the
`google-genai` SDK even validates this for us. This is what the milestone
spec means by "Return structured JSON responses."

We use `gemini-2.5-flash` (see app/config.py) — the stable, free-tier Gemini
model as of mid-2026. If you're reading this well after that, check
https://ai.google.dev/gemini-api/docs/models for whatever the current
free-tier default is and update GEMINI_MODEL in your .env — nothing else in
this file needs to change.
"""

import json

from google import genai
from google.genai import types
from pydantic import BaseModel
from fastapi import HTTPException

from app.config import settings


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/apikey and add it to backend/.env "
                "as GEMINI_API_KEY=your-key-here, then restart the server."
            ),
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _generate_structured(prompt: str, schema: type[BaseModel]):
    """
    Sends `prompt` to Gemini, constrained to return JSON matching `schema`.
    Returns a validated instance of `schema`. Raises HTTPException(502) with
    a beginner-readable message if Gemini errors out or returns unparseable
    output (e.g. API key invalid, quota exceeded, network issue).
    """
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
    except Exception as exc:  # Gemini SDK errors (auth, quota, network) all land here
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API request failed: {exc}. Check your GEMINI_API_KEY and free-tier quota.",
        )

    try:
        return schema.model_validate_json(response.text)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=502,
            detail="Gemini returned a response that didn't match the expected format. Try again.",
        )


# ---------------------------------------------------------------------------
# Response schemas — one per feature, kept small and specific on purpose so
# each prompt has exactly one job.
# ---------------------------------------------------------------------------

class BulletRewrite(BaseModel):
    original: str
    improved: str
    explanation: str


class BulletListResult(BaseModel):
    bullets: list[BulletRewrite]


class SummaryResult(BaseModel):
    summary: str


class CoverLetterResult(BaseModel):
    cover_letter: str


class ATSOptimizationResult(BaseModel):
    optimized_summary: str
    keyword_suggestions: list[str]
    formatting_suggestions: list[str]


class ResumeImprovementResult(BaseModel):
    overall_feedback: str
    improved_summary: str
    improved_experience_bullets: list[BulletRewrite]
    improved_project_bullets: list[BulletRewrite]
    suggested_skills_to_add: list[str]


# ---------------------------------------------------------------------------
# Public functions — one per Milestone 10 feature. Routes call these directly.
# ---------------------------------------------------------------------------

def rewrite_bullet_point(bullet_text: str) -> BulletRewrite:
    prompt = f"""You are a professional resume writer. Rewrite the following resume
bullet point to use a strong action verb, quantify impact where plausible, and
remove weak phrases ("responsible for", "helped with", etc). Keep it to one line.

Original bullet point:
\"\"\"{bullet_text}\"\"\"

Return JSON with: original (the input, unchanged), improved (your rewrite),
explanation (one sentence on what you changed and why)."""
    return _generate_structured(prompt, BulletRewrite)


def rewrite_bullets(bullet_texts: list[str]) -> BulletListResult:
    joined = "\n".join(f"- {b}" for b in bullet_texts)
    prompt = f"""You are a professional resume writer. Rewrite each of the following
resume bullet points to use a strong action verb, quantify impact where
plausible, and remove weak phrases ("responsible for", "helped with", etc).

Bullet points:
{joined}

Return JSON with a "bullets" array. One object per input bullet, each with:
original (the input line, unchanged), improved (your rewrite), explanation
(one sentence on what you changed and why)."""
    return _generate_structured(prompt, BulletListResult)


def generate_summary(resume_text: str) -> SummaryResult:
    prompt = f"""You are a professional resume writer. Based on the resume text below,
write a concise, compelling 2-3 sentence professional summary suitable for the
top of a resume. Write in third person without pronouns, focus on the
candidate's strongest skills and experience.

Resume text:
\"\"\"{resume_text}\"\"\"

Return JSON with a single field: summary."""
    return _generate_structured(prompt, SummaryResult)


def generate_cover_letter(resume_text: str, job_description_text: str, company_name: str = "") -> CoverLetterResult:
    company_line = f"The company is {company_name}." if company_name else ""
    prompt = f"""You are a professional career coach. Write a concise, personalized
cover letter (3-4 short paragraphs) for the candidate described below, tailored
to the job description provided. {company_line} Reference specific skills and
experience from the resume that match what the job description asks for. Do
not invent facts not present in the resume.

Resume text:
\"\"\"{resume_text}\"\"\"

Job description:
\"\"\"{job_description_text}\"\"\"

Return JSON with a single field: cover_letter (the full letter text, with
paragraph breaks as \\n\\n)."""
    return _generate_structured(prompt, CoverLetterResult)


def optimize_for_ats(resume_text: str, missing_skills: list[str]) -> ATSOptimizationResult:
    missing = ", ".join(missing_skills) if missing_skills else "none identified"
    prompt = f"""You are an ATS (Applicant Tracking System) optimization expert. Given
the resume text below and this list of skills a target job wants but the
resume doesn't clearly show: {missing}

Suggest how to naturally work relevant missing skills into the resume
(only ones the candidate plausibly already has some exposure to based on
context — never suggest fabricating experience), plus general ATS formatting
fixes.

Resume text:
\"\"\"{resume_text}\"\"\"

Return JSON with: optimized_summary (a rewritten 2-3 sentence summary that
better targets ATS keyword matching), keyword_suggestions (list of specific
keyword phrases to add), formatting_suggestions (list of structural/formatting
fixes, e.g. section headers, bullet usage)."""
    return _generate_structured(prompt, ATSOptimizationResult)


def improve_resume(resume_text: str, experience_bullets: list[str], project_bullets: list[str],
                    job_description_text: str = "") -> ResumeImprovementResult:
    jd_context = (
        f"\n\nTailor suggestions toward this job description:\n\"\"\"{job_description_text}\"\"\""
        if job_description_text else ""
    )
    experience_joined = "\n".join(f"- {b}" for b in experience_bullets) or "(none detected)"
    projects_joined = "\n".join(f"- {b}" for b in project_bullets) or "(none detected)"

    prompt = f"""You are an expert resume reviewer. Review the resume below and improve
it end-to-end.{jd_context}

Full resume text:
\"\"\"{resume_text}\"\"\"

Experience bullet points:
{experience_joined}

Project bullet points:
{projects_joined}

Return JSON with: overall_feedback (2-3 sentences of high-level feedback),
improved_summary (a rewritten professional summary), improved_experience_bullets
(array of {{original, improved, explanation}} for each experience bullet given),
improved_project_bullets (same shape, for each project bullet given),
suggested_skills_to_add (list of skills worth adding if the candidate
plausibly has them based on context — never fabricate)."""
    return _generate_structured(prompt, ResumeImprovementResult)
