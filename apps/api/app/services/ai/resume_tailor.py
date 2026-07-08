"""Tailors the user's master resume to a specific job description.

Hard constraint: the AI may only rephrase, reorder, and emphasize content
that already exists in the master resume. It must never invent employers,
titles, dates, skills, or metrics that are not present in the source.
"""

from __future__ import annotations

from app.services.ai.provider import get_ai_provider

_SYSTEM_PROMPT = """You are an expert ATS resume writer. You tailor resumes to specific \
job descriptions while being STRICTLY TRUTHFUL.

Rules you must never break:
1. Never invent employers, job titles, dates, degrees, certifications, or skills that are \
not present in the candidate's master resume.
2. You MAY rephrase bullet points, reorder sections, and surface existing skills/keywords \
from the job description if the candidate's resume already demonstrates them.
3. You MAY improve wording, quantify existing achievements only if a number is already \
given in the source text, and adjust emphasis to match the job's priorities.
4. If the job requires a skill the candidate's resume does not support, do NOT add it — \
list it in "missing_skills" instead so the app can surface it to the candidate honestly.
5. Output must be valid JSON matching the requested schema exactly."""

_USER_TEMPLATE = """MASTER RESUME (ground truth — do not exceed this content):
---
{master_resume_text}
---

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
---
{job_description}
---

Produce a tailored resume as JSON with this exact schema:
{{
  "summary": "2-3 sentence professional summary tailored to this job, built only from \
the master resume's real experience",
  "skills": ["ordered list of the candidate's real skills, most relevant to this job first"],
  "experience": [
    {{
      "company": "...",
      "title": "...",
      "dates": "...",
      "bullets": ["rewritten/reordered bullet points using only real content, optimized \
for ATS keywords found in the job description"]
    }}
  ],
  "education": [{{"institution": "...", "degree": "...", "dates": "..."}}],
  "certifications": ["..."],
  "keywords_added": ["job-description keywords now emphasized in this tailored version"],
  "missing_skills": ["skills the job wants that the master resume does not support"]
}}"""


async def tailor_resume(
    master_resume_text: str,
    job_title: str,
    company: str,
    job_description: str,
) -> dict:
    provider = get_ai_provider()
    prompt = _USER_TEMPLATE.format(
        master_resume_text=master_resume_text,
        job_title=job_title,
        company=company,
        job_description=job_description,
    )
    result = await provider.complete_json(prompt, system=_SYSTEM_PROMPT, max_tokens=3000)
    result.setdefault("keywords_added", [])
    result.setdefault("missing_skills", [])
    return result
