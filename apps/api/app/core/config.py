from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = "change_me_to_a_random_secret"
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    # Database
    database_url: str = "postgresql+asyncpg://jobplatform:change_me@localhost:5432/jobplatform"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Clerk auth
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""

    # AI providers
    ai_provider: Literal["openai", "anthropic", "gemini"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # Storage
    storage_backend: Literal["s3", "cloudinary"] = "s3"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "job-platform-documents"
    cloudinary_url: str = ""

    # Notifications - Email
    email_backend: Literal["smtp", "ses"] = "smtp"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "notifications@yourdomain.com"

    # Notifications - WhatsApp (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    notify_whatsapp_to: str = ""

    # Notifications - Web push
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:you@yourdomain.com"

    # Job source connectors
    greenhouse_board_tokens: str = ""
    lever_company_slugs: str = ""
    ashby_job_board_names: str = ""
    smartrecruiters_company_ids: str = ""
    workday_tenants: str = ""
    indeed_publisher_id: str = ""

    # Job search behavior
    job_scan_interval_minutes: int = 30
    job_max_age_hours: int = 24

    @property
    def greenhouse_tokens_list(self) -> list[str]:
        return [t.strip() for t in self.greenhouse_board_tokens.split(",") if t.strip()]

    @property
    def lever_slugs_list(self) -> list[str]:
        return [s.strip() for s in self.lever_company_slugs.split(",") if s.strip()]

    @property
    def ashby_boards_list(self) -> list[str]:
        return [b.strip() for b in self.ashby_job_board_names.split(",") if b.strip()]

    @property
    def smartrecruiters_ids_list(self) -> list[str]:
        return [i.strip() for i in self.smartrecruiters_company_ids.split(",") if i.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
