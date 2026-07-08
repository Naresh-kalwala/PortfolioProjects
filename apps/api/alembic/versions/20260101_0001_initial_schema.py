"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

job_source_enum = postgresql.ENUM(
    "greenhouse", "lever", "ashby", "smartrecruiters", "workday",
    "microsoft_careers", "google_careers", "company_page",
    "linkedin", "indeed", "dice", "ziprecruiter", "wellfound",
    name="jobsourceplatform",
)
workplace_type_enum = postgresql.ENUM("remote", "hybrid", "onsite", name="workplacetype")
employment_type_enum = postgresql.ENUM(
    "contract", "full_time", "part_time", "internship", name="employmenttype"
)
experience_level_enum = postgresql.ENUM("entry", "mid", "senior", name="experiencelevel")
application_status_enum = postgresql.ENUM(
    "new", "summarized", "resume_generated", "cover_letter_generated",
    "ready_to_apply", "auto_applying", "manual_action_required",
    "submitted", "interview", "offer", "rejected", "withdrawn",
    name="applicationstatus",
)
application_method_enum = postgresql.ENUM("auto", "manual_assist", name="applicationmethod")
notification_channel_enum = postgresql.ENUM(
    "email", "whatsapp", "browser_push", name="notificationchannel"
)
notification_type_enum = postgresql.ENUM(
    "high_match_job", "resume_ready", "cover_letter_ready",
    "application_submitted", "manual_action_required", "interview_detected",
    name="notificationtype",
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (
        job_source_enum, workplace_type_enum, employment_type_enum,
        experience_level_enum, application_status_enum, application_method_enum,
        notification_channel_enum, notification_type_enum,
    ):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("clerk_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("portfolio_url", sa.String(500), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("work_history", sa.JSON, nullable=False),
        sa.Column("education", sa.JSON, nullable=False),
        sa.Column("skills", sa.JSON, nullable=False),
        sa.Column("certifications", sa.JSON, nullable=False),
        sa.Column("preferred_locations", sa.JSON, nullable=False),
        sa.Column("predefined_answers", sa.JSON, nullable=False),
        sa.Column("salary_expectation_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("salary_expectation_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("salary_currency", sa.String(10), nullable=False),
        sa.Column("work_authorization", sa.String(255), nullable=True),
        sa.Column("visa_status", sa.String(255), nullable=True),
        sa.Column("requires_stem_opt", sa.Boolean, nullable=False),
        sa.Column("auto_submit_applications", sa.Boolean, nullable=False),
        sa.Column("whatsapp_number", sa.String(50), nullable=True),
        sa.Column("notification_preferences", sa.JSON, nullable=False),
        sa.Column("push_subscriptions", sa.JSON, nullable=False),
        sa.UniqueConstraint("clerk_user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_profiles_clerk_user_id", "user_profiles", ["clerk_user_id"])
    op.create_index("ix_user_profiles_email", "user_profiles", ["email"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", job_source_enum, nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("dedupe_hash", sa.String(64), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("company_logo_url", sa.String(1000), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("workplace_type", workplace_type_enum, nullable=True),
        sa.Column("employment_type", employment_type_enum, nullable=True),
        sa.Column("experience_level", experience_level_enum, nullable=True),
        sa.Column("is_stem_opt_friendly", sa.Boolean, nullable=True),
        sa.Column("is_us_based", sa.Boolean, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("requirements", sa.JSON, nullable=False),
        sa.Column("preferred_qualifications", sa.JSON, nullable=False),
        sa.Column("salary_range", sa.String(255), nullable=True),
        sa.Column("apply_url", sa.String(1000), nullable=False),
        sa.Column("supports_auto_apply", sa.Boolean, nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_data", sa.JSON, nullable=False),
        sa.UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
    )
    op.create_index("ix_jobs_source", "jobs", ["source"])
    op.create_index("ix_jobs_external_id", "jobs", ["external_id"])
    op.create_index("ix_jobs_dedupe_hash", "jobs", ["dedupe_hash"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index("ix_jobs_posted_at", "jobs", ["posted_at"])

    op.create_table(
        "master_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False),
        sa.Column("structured_content", sa.JSON, nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("original_file_key", sa.String(1000), nullable=True),
        sa.Column("original_file_type", sa.String(20), nullable=True),
    )
    op.create_index("ix_master_resumes_user_id", "master_resumes", ["user_id"])

    op.create_table(
        "tailored_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("master_resume_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("master_resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("structured_content", sa.JSON, nullable=False),
        sa.Column("keywords_added", sa.JSON, nullable=False),
        sa.Column("ai_model_used", sa.String(100), nullable=True),
        sa.Column("pdf_file_key", sa.String(1000), nullable=True),
        sa.Column("docx_file_key", sa.String(1000), nullable=True),
        sa.Column("performance_note", sa.Text, nullable=True),
    )
    op.create_index("ix_tailored_resumes_user_id", "tailored_resumes", ["user_id"])

    op.create_table(
        "cover_letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("ai_model_used", sa.String(100), nullable=True),
        sa.Column("pdf_file_key", sa.String(1000), nullable=True),
        sa.Column("docx_file_key", sa.String(1000), nullable=True),
    )
    op.create_index("ix_cover_letters_user_id", "cover_letters", ["user_id"])

    op.create_table(
        "user_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_score", sa.Integer, nullable=True),
        sa.Column("match_breakdown", sa.JSON, nullable=False),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("ai_match_explanation", sa.Text, nullable=True),
        sa.Column("missing_skills", sa.JSON, nullable=False),
        sa.Column("resume_improvement_suggestions", sa.JSON, nullable=False),
        sa.Column("status", application_status_enum, nullable=False),
        sa.Column("application_method", application_method_enum, nullable=True),
        sa.Column("manual_action_reason", sa.Text, nullable=True),
        sa.Column("manual_action_steps", sa.JSON, nullable=False),
        sa.Column("resume_application_url", sa.String(1000), nullable=True),
        sa.Column("is_saved", sa.Boolean, nullable=False),
        sa.Column("is_favorite", sa.Boolean, nullable=False),
        sa.Column("tailored_resume_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("tailored_resumes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cover_letter_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )
    op.create_index("ix_user_jobs_user_id", "user_jobs", ["user_id"])
    op.create_index("ix_user_jobs_job_id", "user_jobs", ["job_id"])
    op.create_index("ix_user_jobs_status", "user_jobs", ["status"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("channel", notification_channel_enum, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("related_job_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_error", sa.Text, nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("user_jobs")
    op.drop_table("cover_letters")
    op.drop_table("tailored_resumes")
    op.drop_table("master_resumes")
    op.drop_table("jobs")
    op.drop_table("user_profiles")

    bind = op.get_bind()
    for enum in (
        notification_type_enum, notification_channel_enum, application_method_enum,
        application_status_enum, experience_level_enum, employment_type_enum,
        workplace_type_enum, job_source_enum,
    ):
        enum.drop(bind, checkfirst=True)
