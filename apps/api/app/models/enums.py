import enum


class JobSourcePlatform(str, enum.Enum):
    # Full search + auto-apply supported (public/structured APIs).
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    SMARTRECRUITERS = "smartrecruiters"
    WORKDAY = "workday"
    MICROSOFT_CAREERS = "microsoft_careers"
    GOOGLE_CAREERS = "google_careers"
    COMPANY_PAGE = "company_page"

    # Search aggregation only — auto-apply intentionally NOT implemented
    # because these platforms' Terms of Service prohibit automated
    # scraping/submission. Applications route to "manual action required".
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    DICE = "dice"
    ZIPRECRUITER = "ziprecruiter"
    WELLFOUND = "wellfound"


# Platforms where our automation is allowed to submit an application directly.
AUTO_APPLY_CAPABLE_PLATFORMS = {
    JobSourcePlatform.GREENHOUSE,
    JobSourcePlatform.LEVER,
    JobSourcePlatform.ASHBY,
    JobSourcePlatform.SMARTRECRUITERS,
}


class WorkplaceType(str, enum.Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class EmploymentType(str, enum.Enum):
    CONTRACT = "contract"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"


class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"


class ApplicationStatus(str, enum.Enum):
    NEW = "new"
    SUMMARIZED = "summarized"
    RESUME_GENERATED = "resume_generated"
    COVER_LETTER_GENERATED = "cover_letter_generated"
    READY_TO_APPLY = "ready_to_apply"
    AUTO_APPLYING = "auto_applying"
    MANUAL_ACTION_REQUIRED = "manual_action_required"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationMethod(str, enum.Enum):
    AUTO = "auto"
    MANUAL_ASSIST = "manual_assist"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    BROWSER_PUSH = "browser_push"


class NotificationType(str, enum.Enum):
    HIGH_MATCH_JOB = "high_match_job"
    RESUME_READY = "resume_ready"
    COVER_LETTER_READY = "cover_letter_ready"
    APPLICATION_SUBMITTED = "application_submitted"
    MANUAL_ACTION_REQUIRED = "manual_action_required"
    INTERVIEW_DETECTED = "interview_detected"
