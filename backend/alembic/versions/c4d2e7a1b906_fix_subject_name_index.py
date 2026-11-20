"""Allow subject names to repeat across course scopes.

Revision ID: c4d2e7a1b906
Revises: f7a6c4310d2b
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d2e7a1b906"
down_revision: Union[str, Sequence[str], None] = "f7a6c4310d2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    indexes = {
        index["name"]: index
        for index in sa.inspect(op.get_bind()).get_indexes("subjects")
        if index.get("name")
    }
    name_index = indexes.get("ix_subjects_name")
    if name_index:
        if name_index.get("unique"):
            op.drop_index("ix_subjects_name", table_name="subjects")
            op.create_index(
                "ix_subjects_name",
                "subjects",
                ["name"],
                unique=False,
            )
    else:
        op.create_index(
            "ix_subjects_name",
            "subjects",
            ["name"],
            unique=False,
        )


def downgrade() -> None:
    duplicate = op.get_bind().execute(
        sa.text(
            "SELECT name FROM subjects GROUP BY name HAVING count(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate:
        raise RuntimeError(
            "Cannot restore the globally unique subject-name index while "
            "duplicate names exist across course scopes."
        )

    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes("subjects")
        if index.get("name")
    }
    if "ix_subjects_name" in indexes:
        op.drop_index("ix_subjects_name", table_name="subjects")
    op.create_index(
        "ix_subjects_name",
        "subjects",
        ["name"],
        unique=True,
    )
