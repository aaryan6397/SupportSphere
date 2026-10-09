"""add hashed API tokens

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa


revision = "f5a6b7c8d9e0"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("api_tokens", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("token_prefix", sa.String(length=16), nullable=False), sa.Column("token_hash", sa.String(length=64), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("last_used_at", sa.DateTime(), nullable=True), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("token_hash"), sa.UniqueConstraint("token_prefix"))
    op.create_index("ix_api_tokens_token_prefix", "api_tokens", ["token_prefix"])
    op.create_index("ix_api_tokens_user_id", "api_tokens", ["user_id"])


def downgrade():
    op.drop_index("ix_api_tokens_user_id", table_name="api_tokens")
    op.drop_index("ix_api_tokens_token_prefix", table_name="api_tokens")
    op.drop_table("api_tokens")
