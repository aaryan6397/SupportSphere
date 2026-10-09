"""add knowledge base articles

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa


revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("knowledge_articles", sa.Column("id", sa.Integer(), nullable=False), sa.Column("title", sa.String(length=200), nullable=False), sa.Column("slug", sa.String(length=140), nullable=False), sa.Column("category", sa.String(length=80), nullable=False), sa.Column("summary", sa.String(length=400), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_by_id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("slug"))
    op.create_index("ix_knowledge_articles_slug", "knowledge_articles", ["slug"])
    op.create_index("ix_knowledge_articles_category", "knowledge_articles", ["category"])
    op.create_index("ix_knowledge_articles_is_published", "knowledge_articles", ["is_published"])


def downgrade():
    op.drop_index("ix_knowledge_articles_is_published", table_name="knowledge_articles")
    op.drop_index("ix_knowledge_articles_category", table_name="knowledge_articles")
    op.drop_index("ix_knowledge_articles_slug", table_name="knowledge_articles")
    op.drop_table("knowledge_articles")
