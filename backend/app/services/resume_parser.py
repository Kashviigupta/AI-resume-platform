"""
Heuristic, section-header-based resume parser.

Why heuristics instead of spaCy/NLTK NER here: resumes have wildly inconsistent
formatting, but almost all of them use a recognizable header ("Experience",
"Skills", etc.) to separate sections. Splitting on those headers is fast,
has zero extra dependencies to install, and — importantly for a learning
project — is easy to read and debug line by line. spaCy/NLTK stay listed in
requirements.txt for when you want to extend this (e.g. NER-based name/date
extraction); this function is where you'd plug that in later.
"""

import json
import re

SECTION_HEADERS = {
    "education": ["education", "academic background", "academics", "educational qualifications"],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "internship", "internships",
    ],
    "skills": ["skills", "technical skills", "core competencies", "skills and tools", "skills & tools"],
    "projects": ["projects", "academic projects", "personal projects", "key projects"],
    "certifications": [
        "certifications", "certificates", "licenses and certifications", "licenses & certifications",
    ],
}


def _detect_header(line: str):
    """Returns the section name if `line` looks like one of our known headers, else None."""
    clean = line.strip().lower().strip(":")
    if not clean or len(clean) > 40:
        return None
    for section, keywords in SECTION_HEADERS.items():
        if clean in keywords:
            return section
    return None


def _split_skills(skills_text: str) -> list:
    """Turns a blob like 'Python, React | SQL\\nGit' into ['Python', 'React', 'SQL', 'Git']."""
    if not skills_text.strip():
        return []
    raw_items = re.split(r"[,|•;\n]", skills_text)
    return [item.strip() for item in raw_items if item.strip()]


def parse_resume_sections(raw_text: str) -> dict:
    """
    Walks the resume line by line. Whenever a line matches a known section
    header, everything after it (until the next header) is attributed to
    that section — this is the whole algorithm.
    """
    lines = raw_text.splitlines()
    sections = {key: [] for key in SECTION_HEADERS}
    current_section = None

    for line in lines:
        header = _detect_header(line)
        if header:
            current_section = header
            continue
        if current_section and line.strip():
            sections[current_section].append(line.strip())

    skills_list = _split_skills("\n".join(sections["skills"]))

    return {
        "education": sections["education"],
        "experience": sections["experience"],
        "skills": skills_list,
        "projects": sections["projects"],
        "certifications": sections["certifications"],
        "sections_found": [k for k, v in sections.items() if v],
    }


def sections_to_json(parsed: dict) -> str:
    return json.dumps(parsed)
