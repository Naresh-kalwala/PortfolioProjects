from __future__ import annotations

from app.services.ai.provider import get_ai_provider

_SYSTEM_PROMPT = """You summarize job postings concisely and accurately for a busy job \
seeker skimming a dashboard. Never editorialize beyond what the posting states."""

_SUMMARY_TEMPLATE = """Summarize this job posting in 3-4 sentences covering: what the \
role actually does day-to-day, the must-have qualifications, and anything notable about \
compensation, visa sponsorship, or work arrangement if mentioned.

JOB TITLE: {job_title}
COMPANY: {company}
DESCRIPTION:
---
{job_description}
---

Return only the summary text, no headers, no markdown."""


async def summarize_job(job_title: str, company: str, job_description: str) -> str:
    provider = get_ai_provider()
    prompt = _SUMMARY_TEMPLATE.format(
        job_title=job_title, company=company, job_description=job_description
    )
    return (await provider.complete(prompt, system=_SYSTEM_PROMPT, max_tokens=400)).strip()
