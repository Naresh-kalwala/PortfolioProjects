from app.services.job_sources.ashby import AshbyConnector
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.google_careers import GoogleCareersConnector
from app.services.job_sources.greenhouse import GreenhouseConnector
from app.services.job_sources.lever import LeverConnector
from app.services.job_sources.microsoft_careers import MicrosoftCareersConnector
from app.services.job_sources.smartrecruiters import SmartRecruitersConnector
from app.services.job_sources.workday import WorkdayConnector

# Connectors that poll a platform's own public/official API on a schedule.
# LinkedIn/Indeed/Dice/ZipRecruiter/Wellfound are intentionally excluded —
# see manual_paste.py for how those platforms are handled instead.
ACTIVE_CONNECTORS: list[type[JobSourceConnector]] = [
    GreenhouseConnector,
    LeverConnector,
    AshbyConnector,
    SmartRecruitersConnector,
    WorkdayConnector,
    MicrosoftCareersConnector,
    GoogleCareersConnector,
]

__all__ = [
    "JobSourceConnector",
    "NormalizedJob",
    "ACTIVE_CONNECTORS",
    "GreenhouseConnector",
    "LeverConnector",
    "AshbyConnector",
    "SmartRecruitersConnector",
    "WorkdayConnector",
    "MicrosoftCareersConnector",
    "GoogleCareersConnector",
]
