"""add password reset token version

Revision ID: a6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a6b7c8d9e0f1"
down_revision = "f5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("password_reset_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("password_reset_version")
