"""Reconcile schema drift after the legacy validation revision

Revision ID: f7a6c4310d2b
Revises: e7b6c1a9f204
Create Date: 2026-11-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a6c4310d2b"
down_revision: Union[str, Sequence[str], None] = "e7b6c1a9f204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table_name: str) -> set:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set:
    return {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
        if index.get("name")
    }


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    for column in (
        sa.Column("course", sa.String(length=100), nullable=True),
        sa.Column("curriculum", sa.String(length=150), nullable=True),
        sa.Column("academic_year", sa.String(length=20), nullable=True),
    ):
        _add_column_if_missing("subjects", column)

    if "ix_subjects_course" not in _indexes("subjects"):
        op.create_index("ix_subjects_course", "subjects", ["course"], unique=False)
    if "uq_subject_course_scope" not in _indexes("subjects"):
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

    for column in (
        sa.Column("course", sa.String(length=100), nullable=True),
        sa.Column("curriculum", sa.String(length=150), nullable=True),
        sa.Column("academic_year", sa.String(length=20), nullable=True),
    ):
        _add_column_if_missing("study_materials", column)
    if "ix_study_materials_course" not in _indexes("study_materials"):
        op.create_index(
            "ix_study_materials_course",
            "study_materials",
            ["course"],
            unique=False,
        )

    if "request_type" not in _columns("counselling_requests"):
        op.add_column(
            "counselling_requests",
            sa.Column("request_type", sa.String(length=50), nullable=True),
        )
    op.execute(
        "UPDATE counselling_requests SET request_type = 'higher_studies' "
        "WHERE request_type IS NULL"
    )
    op.alter_column(
        "counselling_requests",
        "request_type",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    _add_column_if_missing(
        "study_groups",
        sa.Column("class_id", sa.Integer(), nullable=True),
    )
    _add_column_if_missing(
        "study_groups",
        sa.Column("created_by", sa.Integer(), nullable=True),
    )
    existing_group_fks = sa.inspect(op.get_bind()).get_foreign_keys("study_groups")
    group_fk_targets = {
        (tuple(fk["constrained_columns"]), fk["referred_table"], (fk.get("options", {}).get("ondelete") or "").upper())
        for fk in existing_group_fks
    }
    if (("class_id",), "study_classes", "SET NULL") not in group_fk_targets:
        op.create_foreign_key(
            "fk_study_groups_class_id",
            "study_groups",
            "study_classes",
            ["class_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if (("created_by",), "students", "SET NULL") not in group_fk_targets:
        op.create_foreign_key(
            "fk_study_groups_created_by",
            "study_groups",
            "students",
            ["created_by"],
            ["id"],
            ondelete="SET NULL",
        )
    if "ix_study_groups_class_id" not in _indexes("study_groups"):
        op.create_index(
            "ix_study_groups_class_id",
            "study_groups",
            ["class_id"],
            unique=False,
        )

    if "study_mode" not in _columns("study_schedules"):
        op.add_column(
            "study_schedules",
            sa.Column("study_mode", sa.String(length=20), nullable=True),
        )
    op.execute("UPDATE study_schedules SET study_mode = 'online' WHERE study_mode IS NULL")
    op.alter_column(
        "study_schedules",
        "study_mode",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default=None,
    )

    topic_id_column = next(
        column
        for column in sa.inspect(op.get_bind()).get_columns("teaching_pairs")
        if column["name"] == "topic_id"
    )
    if not topic_id_column["nullable"]:
        op.alter_column(
            "teaching_pairs",
            "topic_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
    topic_fk = next(
        (
            foreign_key
            for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys("teaching_pairs")
            if foreign_key["constrained_columns"] == ["topic_id"]
        ),
        None,
    )
    if topic_fk and (topic_fk.get("options", {}).get("ondelete") or "").upper() != "SET NULL":
        op.drop_constraint(topic_fk["name"], "teaching_pairs", type_="foreignkey")
        topic_fk = None
    if not topic_fk:
        op.create_foreign_key(
            "teaching_pairs_topic_id_fkey",
            "teaching_pairs",
            "topics",
            ["topic_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if "approval_status" not in _columns("tests"):
        op.add_column(
            "tests",
            sa.Column("approval_status", sa.String(length=20), nullable=True),
        )
    op.execute("UPDATE tests SET approval_status = 'approved' WHERE approval_status IS NULL")
    op.alter_column(
        "tests",
        "approval_status",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="pending",
    )


def downgrade() -> None:
    raise NotImplementedError(
        "Schema reconciliation is intentionally irreversible because it "
        "repairs objects already present outside the recorded migration history."
    )
