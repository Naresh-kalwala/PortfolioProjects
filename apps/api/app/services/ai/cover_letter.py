from __future__ import annotations

from app.services.ai.provider import get_ai_provider

_SYSTEM_PROMPT = """You are an expert cover letter writer. Write natural, professional, \
non-generic cover letters that sound like a real person wrote them — no cliches like \
"I am excited to apply" repeated everywhere, no invented facts about the candidate."""

_USER_TEMPLATE = """Write a cover letter for this candidate applying to this job.

CANDIDATE BACKGROUND (ground truth, do not exceed):
---
{master_resume_text}
---

CANDIDATE NAME: {full_name}

COMPANY: {company}
JOB TITLE: {job_title}
JOB DESCRIPTION:
---
{job_description}
---

Requirements:
- Address the company by name and reference something specific about the role.
- Highlight relevant experience with Power BI, SQL, Power Platform (Power Apps/Power \
Automate), Microsoft Fabric, Tableau, analytics, dashboards, and reporting WHERE the \
candidate's background actually supports it — never fabricate experience.
- 3-4 paragraphs, professional but natural tone, no more than 350 words.
- Do not use placeholder brackets like [Company Name] — use the real values given above.
- Sign off with the candidate's name.

Return only the plain text of the letter, no markdown, no JSON."""


async def generate_cover_letter(
    master_resume_text: str,
    full_name: str,
    company: str,
    job_title: str,
    job_description: str,
) -> str:
    provider = get_ai_provider()
    prompt = _USER_TEMPLATE.format(
        master_resume_text=master_resume_text,
        full_name=full_name or "the candidate",
        company=company,
        job_title=job_title,
        job_description=job_description,
    )
    return (await provider.complete(prompt, system=_SYSTEM_PROMPT, max_tokens=1200)).strip()
