TARGET_ROLE_KEYWORDS = [
    "power bi developer",
    "power bi",
    "power platform developer",
    "power apps developer",
    "power apps",
    "power automate developer",
    "power automate",
    "microsoft fabric developer",
    "microsoft fabric",
    "data analyst",
    "business intelligence analyst",
    "bi developer",
    "bi analyst",
    "sql developer",
    "data visualization developer",
    "data visualization",
]


def is_relevant_job(title: str, description: str = "") -> bool:
    haystack = f"{title} {description[:500]}".lower()
    return any(keyword in haystack for keyword in TARGET_ROLE_KEYWORDS)
