from __future__ import annotations

from app.services.ai.provider import get_ai_provider

_SYSTEM_PROMPT = """You are an ATS matching engine. You objectively score how well a \
candidate's resume matches a job description across five weighted dimensions. Be honest \
and critical — do not inflate scores. Base every judgment only on the resume text given."""

_USER_TEMPLATE = """CANDIDATE RESUME:
---
{master_resume_text}
---

JOB DESCRIPTION:
---
{job_description}
---

REQUIRED QUALIFICATIONS:
{requirements}

PREFERRED QUALIFICATIONS:
{preferred_qualifications}

Score the match as JSON with this exact schema:
{{
  "overall_score": <integer 0-100>,
  "breakdown": {{
    "skills": <integer 0-100>,
    "experience": <integer 0-100>,
    "keywords": <integer 0-100>,
    "responsibilities": <integer 0-100>,
    "required_qualifications": <integer 0-100>,
    "preferred_qualifications": <integer 0-100>
  }},
  "explanation": "2-4 sentences explaining why this score was given, referencing specific \
overlaps and gaps",
  "missing_skills": ["skills/qualifications the job needs that the resume does not show"],
  "resume_improvement_suggestions": ["specific, actionable suggestions to improve match"]
}}"""


async def compute_match_score(
    master_resume_text: str,
    job_description: str,
    requirements: list[str],
    preferred_qualifications: list[str],
) -> dict:
    provider = get_ai_provider()
    prompt = _USER_TEMPLATE.format(
        master_resume_text=master_resume_text,
        job_description=job_description,
        requirements="\n".join(f"- {r}" for r in requirements) or "Not specified",
        preferred_qualifications="\n".join(f"- {p}" for p in preferred_qualifications)
        or "Not specified",
    )
    result = await provider.complete_json(prompt, system=_SYSTEM_PROMPT, max_tokens=1500)
    result.setdefault("missing_skills", [])
    result.setdefault("resume_improvement_suggestions", [])
    return result
