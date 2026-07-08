from __future__ import annotations

from app.services.ai.provider import get_ai_provider

_QUESTIONS_SYSTEM = """You are an experienced technical interviewer for data/BI/Power \
Platform roles. Generate realistic interview questions an actual panel would ask."""

_QUESTIONS_TEMPLATE = """Based on this job description, generate likely interview \
questions as JSON:
{{
  "behavioral": ["..."],
  "technical": ["..."],
  "role_specific": ["..."]
}}
5 questions per category.

JOB TITLE: {job_title}
DESCRIPTION:
---
{job_description}
---"""

_ANSWERS_SYSTEM = """You help candidates prepare honest, specific interview answers \
grounded only in their real resume content — never fabricate projects or metrics."""

_ANSWERS_TEMPLATE = """Using ONLY the candidate's real background below, draft a strong \
STAR-format answer to this interview question. If the resume has no directly relevant \
experience, say so and suggest how to honestly bridge the gap using transferable skills.

CANDIDATE BACKGROUND:
---
{master_resume_text}
---

QUESTION: {question}

Return only the answer text, no markdown."""


async def generate_interview_questions(job_title: str, job_description: str) -> dict:
    provider = get_ai_provider()
    prompt = _QUESTIONS_TEMPLATE.format(job_title=job_title, job_description=job_description)
    return await provider.complete_json(prompt, system=_QUESTIONS_SYSTEM, max_tokens=1200)


async def generate_interview_answer(master_resume_text: str, question: str) -> str:
    provider = get_ai_provider()
    prompt = _ANSWERS_TEMPLATE.format(
        master_resume_text=master_resume_text, question=question
    )
    return (await provider.complete(prompt, system=_ANSWERS_SYSTEM, max_tokens=600)).strip()
