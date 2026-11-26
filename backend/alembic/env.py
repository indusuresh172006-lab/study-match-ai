import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Make sure the backend package is on the path so we can import our modules
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from database import Base, DATABASE_URL  # noqa: E402

# Import ALL models so their tables are registered in Base.metadata
import models  # noqa: F401, E402  (side-effect import registers all models)

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point alembic at our SQLAlchemy metadata
target_metadata = Base.metadata

# Override the sqlalchemy.url from alembic.ini with the value from .env
config.set_main_option("sqlalchemy.url", DATABASE_URL.render_as_string(hide_password=False))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        from sqlalchemy import inspect, text

        # Ensure base tables exist if deploying to a brand-new database
        target_metadata.create_all(bind=connection)

        # Check if the database was already created from latest models.py
        inspector = inspect(connection)
        tables = inspector.get_table_names()
        if "subjects" in tables:
            columns = [c["name"] for c in inspector.get_columns("subjects")]
            if "course" in columns:
                # The schema already has the latest columns from models.py
                head_rev = context.get_head_revision() or "f7a6c4310d2b"
                has_alembic = "alembic_version" in tables
                if not has_alembic:
                    connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
                connection.execute(text("DELETE FROM alembic_version"))
                connection.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}')"))
                connection.commit()
                print(f"Database schema already at latest models definition. Stamped Alembic to head: {head_rev}")
                return

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
