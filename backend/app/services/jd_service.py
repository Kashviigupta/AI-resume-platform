"""
Job description matching: how well does a resume line up with a specific JD?

Two independent things are computed here:

1. match_score — an overall 0-100 "similarity" number between the resume text
   and the JD text, using TF-IDF (Term Frequency-Inverse Document Frequency)
   + cosine similarity. This is the same classic technique search engines
   used before embeddings became cheap — it's fast, needs no model download,
   and is easy to explain: words that are common across both documents (and
   rare across documents in general) count more toward "similarity."

2. missing_skills — a much more literal, explainable signal: which specific
   skills does the JD mention that the resume's Skills section doesn't? This
   matters separately from match_score because two documents can have decent
   word overlap while still missing 3-4 skills a recruiter's ATS filters on.

We deliberately do NOT use sentence-transformers here even though it's listed
in the tech stack for later: it requires downloading a multi-hundred-MB model
on first run, which is a bad experience on a slow connection or free-tier
hosting. TF-IDF cosine similarity is the standard "beginner-friendly but still
real" approach and is what this milestone implements. If you want to upgrade
later, swap the vectorizer step in `compute_match_score` for sentence
embeddings — the rest of the pipeline (missing skills, keyword extraction)
doesn't need to change.
"""

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# A deliberately broad, flat vocabulary of common tech/soft skills. Any of
# these words/phrases found in a JD or resume (case-insensitive, word-boundary
# matched) counts as a "skill" for matching purposes. This is the same
# heuristic-over-NLP-model tradeoff as resume_parser.py — plug in spaCy's
# PhraseMatcher here later if you want a much larger vocabulary.
SKILL_VOCAB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "nosql",
    "react", "react.js", "vue", "angular", "node.js", "node", "express",
    "django", "flask", "fastapi", "spring", "spring boot",
    "html", "css", "tailwind", "bootstrap",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "git", "github", "gitlab", "linux",
    "mongodb", "postgresql", "mysql", "sqlite", "redis", "firebase",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "rest api", "graphql", "microservices",
    "agile", "scrum", "jira",
    "leadership", "communication", "teamwork", "problem solving",
    "data structures", "algorithms", "system design", "oop",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "be", "as", "at", "by", "this", "that", "we", "you",
    "will", "our", "your", "have", "has", "who", "it", "from", "their",
}

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z+.#-]*")


def extract_keywords(text: str, top_n: int = 20) -> list[str]:
    """
    Simple keyword frequency extraction: lowercase, strip stopwords/short
    words, count occurrences, return the top_n most frequent words. Used to
    show the user "here's what this JD emphasizes most."
    """
    words = [w.lower() for w in WORD_RE.findall(text)]
    words = [w for w in words if len(w) > 2 and w not in STOPWORDS]

    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1

    ranked = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
    return [word for word, _count in ranked[:top_n]]


def extract_skills(text: str) -> list[str]:
    """Returns every entry in SKILL_VOCAB that appears in `text` (case-insensitive)."""
    lowered = text.lower()
    found = []
    for skill in SKILL_VOCAB:
        # \b word-boundary matching so "java" doesn't match inside "javascript"
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, lowered):
            found.append(skill)
    return found


def compute_match_score(resume_text: str, jd_text: str) -> float:
    """
    TF-IDF vectorizes both documents into the same vector space, then measures
    the cosine of the angle between them (1.0 = identical direction/topic,
    0.0 = no shared vocabulary at all). Scaled to 0-100 for display.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        # Happens if, after removing stopwords, one document has zero
        # remaining vocabulary (e.g. an empty/garbage upload).
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 1)


def find_missing_skills(resume_skills: list[str], jd_skills: list[str]) -> list[str]:
    """Skills the JD mentions that the resume's skill list doesn't cover."""
    resume_set = {s.lower() for s in resume_skills}
    return [skill for skill in jd_skills if skill.lower() not in resume_set]


def analyze_job_description(resume_text: str, resume_skills: list[str], jd_text: str) -> dict:
    """Runs the full JD-matching pipeline and returns everything the API needs."""
    jd_keywords = extract_keywords(jd_text)
    jd_skills = extract_skills(jd_text)
    matched_skills = [s for s in jd_skills if s.lower() in {r.lower() for r in resume_skills}]
    missing_skills = find_missing_skills(resume_skills, jd_skills)
    match_score = compute_match_score(resume_text, jd_text)

    return {
        "match_score": match_score,
        "jd_keywords": jd_keywords,
        "jd_skills_found": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
