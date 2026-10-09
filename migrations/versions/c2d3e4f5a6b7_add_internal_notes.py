"""add internal ticket notes

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa


revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ticket_comments") as batch_op:
        batch_op.add_column(
            sa.Column("is_internal", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade():
    with op.batch_alter_table("ticket_comments") as batch_op:
        batch_op.drop_column("is_internal")
