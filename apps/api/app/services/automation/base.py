from dataclasses import dataclass


@dataclass
class ApplicantContext:
    full_name: str
    email: str
    phone: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    github_url: str | None
    resume_pdf_path: str
    cover_letter_pdf_path: str
    predefined_answers: dict[str, str]
    work_authorization: str | None
    visa_status: str | None
    requires_stem_opt: bool


@dataclass
class AutoApplyResult:
    success: bool
    submitted: bool
    reason: str | None = None
    manual_action_steps: list[str] | None = None
    screenshot_path: str | None = None
