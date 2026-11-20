"""Add course scope to course summaries.

Revision ID: e71a6d9c2b54
Revises: d08c91b4e23f
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e71a6d9c2b54"
down_revision: Union[str, Sequence[str], None] = "d08c91b4e23f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "course_summaries",
        sa.Column("course", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "course_summaries",
        sa.Column("curriculum", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "course_summaries",
        sa.Column("academic_year", sa.String(length=20), nullable=True),
    )
    op.create_index(
        "ix_course_summaries_course",
        "course_summaries",
        ["course"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_course_summaries_course", table_name="course_summaries")
    op.drop_column("course_summaries", "academic_year")
    op.drop_column("course_summaries", "curriculum")
    op.drop_column("course_summaries", "course")
