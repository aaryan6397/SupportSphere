"""add ticket SLA and lifecycle timestamps

Revision ID: b1c2d3e4f5a6
Revises: f7a8ee81a733
Create Date: 2026-10-05
"""

from alembic import op
import sqlalchemy as sa


revision = "b1c2d3e4f5a6"
down_revision = "f7a8ee81a733"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(sa.Column("sla_due_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("first_responded_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("resolved_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_column("resolved_at")
        batch_op.drop_column("first_responded_at")
        batch_op.drop_column("sla_due_at")
