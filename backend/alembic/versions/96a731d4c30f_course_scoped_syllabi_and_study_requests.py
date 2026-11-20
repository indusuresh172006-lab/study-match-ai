"""course-scoped syllabi and study support requests

Revision ID: 96a731d4c30f
Revises: 4caebe829205
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "96a731d4c30f"
down_revision: Union[str, Sequence[str], None] = "4caebe829205"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("course", sa.String(length=100), nullable=True))
    op.add_column("subjects", sa.Column("curriculum", sa.String(length=150), nullable=True))
    op.add_column("subjects", sa.Column("academic_year", sa.String(length=20), nullable=True))
    op.drop_index("ix_subjects_name", table_name="subjects")
    op.create_index("ix_subjects_name", "subjects", ["name"], unique=False)
    op.create_index("ix_subjects_course", "subjects", ["course"], unique=False)
    op.create_index(
        "uq_subject_course_scope",
        "subjects",
        [
            sa.text("lower(name)"),
            sa.text("lower(coalesce(course, ''))"),
            sa.text("lower(coalesce(curriculum, ''))"),
            sa.text("lower(coalesce(academic_year, ''))"),
        ],
        unique=True,
    )
    op.add_column("study_materials", sa.Column("course", sa.String(length=100), nullable=True))
    op.add_column("study_materials", sa.Column("curriculum", sa.String(length=150), nullable=True))
    op.add_column("study_materials", sa.Column("academic_year", sa.String(length=20), nullable=True))
    op.create_index("ix_study_materials_course", "study_materials", ["course"], unique=False)
    op.add_column(
        "counselling_requests",
        sa.Column(
            "request_type",
            sa.String(length=50),
            server_default="higher_studies",
            nullable=False,
        ),
    )
    op.alter_column("counselling_requests", "request_type", server_default=None)


def downgrade() -> None:
    op.drop_column("counselling_requests", "request_type")
    op.drop_index("ix_study_materials_course", table_name="study_materials")
    op.drop_column("study_materials", "academic_year")
    op.drop_column("study_materials", "curriculum")
    op.drop_column("study_materials", "course")
    op.drop_index("uq_subject_course_scope", table_name="subjects")
    op.drop_index("ix_subjects_course", table_name="subjects")
    op.drop_index("ix_subjects_name", table_name="subjects")
    op.create_index("ix_subjects_name", "subjects", ["name"], unique=True)
    op.drop_column("subjects", "academic_year")
    op.drop_column("subjects", "curriculum")
    op.drop_column("subjects", "course")
