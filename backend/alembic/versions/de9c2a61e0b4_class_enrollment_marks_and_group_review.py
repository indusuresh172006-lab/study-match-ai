"""class enrollment, marks import, and teacher-reviewed groups

Revision ID: de9c2a61e0b4
Revises: 96a731d4c30f
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "de9c2a61e0b4"
down_revision: Union[str, Sequence[str], None] = "96a731d4c30f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "study_classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("join_code", sa.String(length=16), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("course", sa.String(length=100), nullable=False),
        sa.Column("curriculum", sa.String(length=150), nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["teacher_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("join_code", name="uq_study_class_join_code"),
    )
    op.create_index("ix_study_classes_id", "study_classes", ["id"], unique=False)

    op.create_table(
        "class_enrollments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["class_id"], ["study_classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("class_id", "student_id", name="uq_class_enrollment"),
    )
    op.create_index("ix_class_enrollments_id", "class_enrollments", ["id"], unique=False)
    op.create_index("ix_class_enrollments_class_id", "class_enrollments", ["class_id"], unique=False)
    op.create_index("ix_class_enrollments_student_id", "class_enrollments", ["student_id"], unique=False)

    op.create_table(
        "mark_import_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("imported_by", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["class_id"], ["study_classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["imported_by"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mark_import_batches_id", "mark_import_batches", ["id"], unique=False)

    op.create_table(
        "imported_marks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["batch_id"], ["mark_import_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_imported_marks_id", "imported_marks", ["id"], unique=False)
    op.create_index("ix_imported_marks_student_id", "imported_marks", ["student_id"], unique=False)

    op.add_column("study_groups", sa.Column("class_id", sa.Integer(), nullable=True))
    op.add_column("study_groups", sa.Column("created_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_study_groups_class_id",
        "study_groups",
        "study_classes",
        ["class_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_study_groups_created_by",
        "study_groups",
        "students",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_study_groups_class_id", "study_groups", ["class_id"], unique=False)

    op.add_column(
        "study_schedules",
        sa.Column("study_mode", sa.String(length=20), nullable=False, server_default="online"),
    )
    op.alter_column("study_schedules", "study_mode", server_default=None)

    op.drop_constraint("teaching_pairs_topic_id_fkey", "teaching_pairs", type_="foreignkey")
    op.alter_column("teaching_pairs", "topic_id", nullable=True)
    op.create_foreign_key(
        "teaching_pairs_topic_id_fkey",
        "teaching_pairs",
        "topics",
        ["topic_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("teaching_pairs_topic_id_fkey", "teaching_pairs", type_="foreignkey")
    op.alter_column("teaching_pairs", "topic_id", nullable=False)
    op.create_foreign_key(
        "teaching_pairs_topic_id_fkey",
        "teaching_pairs",
        "topics",
        ["topic_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("study_schedules", "study_mode")
    op.drop_index("ix_study_groups_class_id", table_name="study_groups")
    op.drop_constraint("fk_study_groups_created_by", "study_groups", type_="foreignkey")
    op.drop_constraint("fk_study_groups_class_id", "study_groups", type_="foreignkey")
    op.drop_column("study_groups", "created_by")
    op.drop_column("study_groups", "class_id")

    op.drop_index("ix_imported_marks_student_id", table_name="imported_marks")
    op.drop_index("ix_imported_marks_id", table_name="imported_marks")
    op.drop_table("imported_marks")
    op.drop_index("ix_mark_import_batches_id", table_name="mark_import_batches")
    op.drop_table("mark_import_batches")
    op.drop_index("ix_class_enrollments_student_id", table_name="class_enrollments")
    op.drop_index("ix_class_enrollments_class_id", table_name="class_enrollments")
    op.drop_index("ix_class_enrollments_id", table_name="class_enrollments")
    op.drop_table("class_enrollments")
    op.drop_index("ix_study_classes_id", table_name="study_classes")
    op.drop_table("study_classes")
