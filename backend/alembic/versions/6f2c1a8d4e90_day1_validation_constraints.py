"""Add Day 1 validation constraints

Revision ID: 6f2c1a8d4e90
Revises: 4caebe829205
Create Date: 2026-11-19
"""

from alembic import op


revision = "6f2c1a8d4e90"
down_revision = "4caebe829205"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE tablename = 'topics'
                  AND indexname = 'uq_topic_subject_name'
            ) THEN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'uq_topic_subject_name'
                ) THEN
                    ALTER TABLE topics
                    ADD CONSTRAINT uq_topic_subject_name UNIQUE (subject_id, name);
                END IF;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_students_role'
            ) THEN
                ALTER TABLE students
                ADD CONSTRAINT ck_students_role
                CHECK (role IN ('student', 'teacher', 'admin'));
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.drop_constraint("ck_students_role", "students", type_="check")
    op.drop_constraint("uq_topic_subject_name", "topics", type_="unique")
