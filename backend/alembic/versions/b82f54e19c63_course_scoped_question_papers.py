"""Add course scope to uploaded question papers.

Revision ID: b82f54e19c63
Revises: e71a6d9c2b54
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b82f54e19c63"
down_revision: Union[str, Sequence[str], None] = "e71a6d9c2b54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "question_papers",
        sa.Column("course", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "question_papers",
        sa.Column("curriculum", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "question_papers",
        sa.Column("academic_year", sa.String(length=20), nullable=True),
    )
    op.create_index(
        "ix_question_papers_course",
        "question_papers",
        ["course"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_question_papers_course", table_name="question_papers")
    op.drop_column("question_papers", "academic_year")
    op.drop_column("question_papers", "curriculum")
    op.drop_column("question_papers", "course")
