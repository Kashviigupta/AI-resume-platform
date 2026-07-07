"""
Two separate, transparent scoring functions:

- compute_ats_score: how likely an Applicant Tracking System is to parse
  this resume correctly and match it on keywords (structure/format focused).
- compute_quality_score: how well the resume is *written* (weak phrases,
  passive voice, personal pronouns, bullet usage).

Both return (score_0_to_100, list_of_human_readable_reasons) so the frontend
can show exactly *why* a resume got the score it did, not just a number.
"""

import re

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "duties included",
    "in charge of", "involved in", "participated in", "assisted with", "tasked with",
]

STRONG_VERB_SUGGESTIONS = ["led", "built", "designed", "implemented", "optimized",
                            "launched", "reduced", "increased", "automated", "delivered"]

EMAIL_RE = re.compile(r"[\w.\-]+@[\w\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s\-]?)?\d{10}")
PASSIVE_RE = re.compile(r"\b(was|were|is|are|been|being)\s+\w+ed\b", re.IGNORECASE)
PRONOUN_RE = re.compile(r"\b(I|me|my|myself)\b")
BULLET_RE = re.compile(r"^\s*[•\-*]\s+", re.MULTILINE)


def compute_ats_score(raw_text: str, parsed: dict) -> tuple[float, list[str]]:
    reasons = []
    score = 0

    has_email = bool(EMAIL_RE.search(raw_text))
    has_phone = bool(PHONE_RE.search(raw_text))
    if has_email and has_phone:
        score += 15
        reasons.append("Contact info (email + phone) detected — good for ATS parsing.")
    elif has_email or has_phone:
        score += 8
        reasons.append("Only one of email/phone was detected — make sure both are clearly visible near the top.")
    else:
        reasons.append("No email or phone number detected — ATS systems may reject resumes without clear contact info.")

    core_sections = ["education", "experience", "skills"]
    found_core = [s for s in core_sections if parsed.get(s)]
    score += len(found_core) * 12  # up to 36
    missing_core = [s for s in core_sections if s not in found_core]
    if missing_core:
        reasons.append(
            f"Missing or unrecognized section(s): {', '.join(missing_core)}. "
            "Use clear headers like 'Experience' and 'Skills'."
        )
    else:
        reasons.append("All core sections (Education, Experience, Skills) were detected.")

    if parsed.get("projects") or parsed.get("certifications"):
        score += 10
        reasons.append("Projects/Certifications section found — good, especially for early-career resumes.")
    else:
        reasons.append("No Projects or Certifications section found — consider adding one to stand out.")

    skill_count = len(parsed.get("skills", []))
    if skill_count >= 8:
        score += 15
        reasons.append(f"{skill_count} skills detected — a strong keyword base for ATS matching.")
    elif skill_count >= 4:
        score += 10
        reasons.append(f"Only {skill_count} skills detected — list more specific tools/technologies.")
    elif skill_count > 0:
        score += 5
        reasons.append(f"Very few skills detected ({skill_count}) — ATS systems match heavily on this section.")
    else:
        reasons.append("No Skills section detected at all — this significantly hurts ATS keyword matching.")

    bullet_count = len(BULLET_RE.findall(raw_text))
    if bullet_count >= 5:
        score += 14
        reasons.append("Bullet points are used consistently — good for ATS and readability.")
    elif bullet_count > 0:
        score += 7
        reasons.append("Some bullet points found, but not consistently — use bullets for every role/project.")
    else:
        reasons.append("No bullet points detected — ATS and recruiters both parse bulleted achievements more easily than paragraphs.")

    word_count = len(raw_text.split())
    if 250 <= word_count <= 900:
        score += 10
        reasons.append(f"Resume length looks appropriate ({word_count} words).")
    elif word_count < 250:
        reasons.append(f"Resume seems short ({word_count} words) — you may be missing detail.")
    else:
        reasons.append(f"Resume seems long ({word_count} words) — consider trimming to about 1-2 pages worth of content.")

    return round(max(0, min(100, score)), 1), reasons


def compute_quality_score(raw_text: str) -> tuple[float, list[str]]:
    suggestions = []
    score = 100.0

    lowered = raw_text.lower()
    weak_hits = [phrase for phrase in WEAK_PHRASES if phrase in lowered]
    if weak_hits:
        score -= min(30, len(weak_hits) * 6)
        examples = ", ".join(f'"{w}"' for w in weak_hits[:3])
        suggestion_verbs = ", ".join(STRONG_VERB_SUGGESTIONS[:5])
        suggestions.append(
            f"Weak phrase(s) found: {examples}. Replace with strong action verbs like {suggestion_verbs}."
        )

    passive_hits = PASSIVE_RE.findall(raw_text)
    if passive_hits:
        score -= min(20, len(passive_hits) * 4)
        suggestions.append(
            f"Detected {len(passive_hits)} instance(s) of passive voice (e.g. 'was assigned'). "
            "Rewrite in active voice: 'Led X' instead of 'Was assigned to lead X.'"
        )

    pronoun_hits = PRONOUN_RE.findall(raw_text)
    if pronoun_hits:
        score -= min(15, len(pronoun_hits) * 3)
        suggestions.append(
            f"Found {len(pronoun_hits)} personal pronoun(s) ('I', 'my'). "
            "Resumes should omit these — start bullets directly with a verb."
        )

    bullet_count = len(BULLET_RE.findall(raw_text))
    if bullet_count == 0:
        score -= 15
        suggestions.append("No bullet points found. Use bullets for experience/projects instead of paragraphs.")

    if not suggestions:
        suggestions.append("No major writing-quality issues detected — nice work!")

    return round(max(0, min(100, score)), 1), suggestions
