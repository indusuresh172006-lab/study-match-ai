"""teacher signup approval and teaching profile details

Revision ID: a9c31d7f0e2b
Revises: b82f54e19c63
Create Date: 2026-11-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9c31d7f0e2b"
down_revision: Union[str, Sequence[str], None] = "b82f54e19c63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column(
            "approval_status",
            sa.String(length=20),
            nullable=False,
            server_default="approved",
        ),
    )
    op.create_check_constraint(
        "ck_students_approval_status",
        "students",
        "approval_status IN ('pending', 'approved', 'rejected')",
    )
    op.add_column("teacher_profiles", sa.Column("subject", sa.String(length=100), nullable=True))
    op.add_column("teacher_profiles", sa.Column("semester", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("teacher_profiles", "semester")
    op.drop_column("teacher_profiles", "subject")
    op.drop_constraint("ck_students_approval_status", "students", type_="check")
    op.drop_column("students", "approval_status")
