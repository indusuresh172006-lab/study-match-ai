"""teacher review workflows for notes and tests, plus guidance activity

Revision ID: e7b6c1a9f204
Revises: de9c2a61e0b4
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7b6c1a9f204"
down_revision: Union[str, Sequence[str], None] = "de9c2a61e0b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "revision_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("subject_name", sa.String(length=100), nullable=False),
        sa.Column("topic_name", sa.String(length=100), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_revision_notes_id", "revision_notes", ["id"], unique=False)

    op.create_table(
        "guidance_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_guidance_activities_id", "guidance_activities", ["id"], unique=False)
    op.create_index(
        "ix_guidance_activities_created_at",
        "guidance_activities",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_guidance_activities_student_id",
        "guidance_activities",
        ["student_id"],
        unique=False,
    )

    op.add_column(
        "tests",
        sa.Column("approval_status", sa.String(length=20), nullable=False, server_default="approved"),
    )
    op.alter_column("tests", "approval_status", server_default="pending")


def downgrade() -> None:
    op.drop_column("tests", "approval_status")
    op.drop_index("ix_guidance_activities_student_id", table_name="guidance_activities")
    op.drop_index("ix_guidance_activities_created_at", table_name="guidance_activities")
    op.drop_index("ix_guidance_activities_id", table_name="guidance_activities")
    op.drop_table("guidance_activities")
    op.drop_index("ix_revision_notes_id", table_name="revision_notes")
    op.drop_table("revision_notes")
