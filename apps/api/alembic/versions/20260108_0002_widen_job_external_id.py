"""widen jobs.external_id

Revision ID: 0002_widen_external_id
Revises: 0001_initial
Create Date: 2026-01-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_widen_external_id"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Manual-paste sources (LinkedIn, Indeed, ...) use the posting's full
    # URL as external_id, which routinely exceeds the original 255-char
    # limit once tracking query params are included, raising
    # StringDataRightTruncation on insert.
    op.alter_column(
        "jobs", "external_id", type_=sa.String(2048), existing_type=sa.String(255)
    )


def downgrade() -> None:
    op.alter_column(
        "jobs", "external_id", type_=sa.String(255), existing_type=sa.String(2048)
    )
