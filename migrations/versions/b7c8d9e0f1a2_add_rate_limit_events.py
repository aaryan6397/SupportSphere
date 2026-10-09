"""add database backed rate limit events

Revision ID: b7c8d9e0f1a2
Revises: a6b7c8d9e0f1
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa


revision = "b7c8d9e0f1a2"
down_revision = "a6b7c8d9e0f1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("rate_limit_events", sa.Column("id", sa.Integer(), nullable=False), sa.Column("action", sa.String(length=50), nullable=False), sa.Column("key_hash", sa.String(length=64), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_rate_limit_events_action", "rate_limit_events", ["action"])
    op.create_index("ix_rate_limit_events_key_hash", "rate_limit_events", ["key_hash"])
    op.create_index("ix_rate_limit_events_created_at", "rate_limit_events", ["created_at"])


def downgrade():
    op.drop_index("ix_rate_limit_events_created_at", table_name="rate_limit_events")
    op.drop_index("ix_rate_limit_events_key_hash", table_name="rate_limit_events")
    op.drop_index("ix_rate_limit_events_action", table_name="rate_limit_events")
    op.drop_table("rate_limit_events")
