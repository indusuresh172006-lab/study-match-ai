"""Add course scope to mock tests.

Revision ID: d08c91b4e23f
Revises: c4d2e7a1b906
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d08c91b4e23f"
down_revision: Union[str, Sequence[str], None] = "c4d2e7a1b906"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tests", sa.Column("course", sa.String(length=100), nullable=True))
    op.add_column("tests", sa.Column("curriculum", sa.String(length=150), nullable=True))
    op.add_column("tests", sa.Column("academic_year", sa.String(length=20), nullable=True))
    op.create_index("ix_tests_course", "tests", ["course"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tests_course", table_name="tests")
    op.drop_column("tests", "academic_year")
    op.drop_column("tests", "curriculum")
    op.drop_column("tests", "course")
