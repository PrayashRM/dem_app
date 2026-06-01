import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from dotenv import load_dotenv

# ─── Path Setup ───────────────────────────────────────────────────────────────
# Add backend root to sys.path so all app imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Load Environment Variables ───────────────────────────────────────────────
load_dotenv()

# ─── Alembic Config ───────────────────────────────────────────────────────────
config = context.config

# ─── Logging Setup ────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ─── Inject DATABASE_URL from environment ─────────────────────────────────────
# This overrides the blank sqlalchemy.url in alembic.ini
# Never hardcode the database URL
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please check your .env file."
    )

config.set_main_option("sqlalchemy.url", database_url)

# ─── Import All Models ────────────────────────────────────────────────────────
# Every model must be imported here so Alembic can detect schema changes.
# If you add a new model file, import it here.
from app.database.db import Base  # noqa: F401 — Base must be imported first
from app.models.user import User  # noqa: F401
from app.models.product import Product  # noqa: F401

# Target metadata for autogenerate support
target_metadata = Base.metadata


# ─── Helpers ──────────────────────────────────────────────────────────────────

def include_object(object, name, type_, reflected, compare_to):
    """
    Control which database objects Alembic tracks.
    Excludes any external/third-party tables that should not be managed here.
    """
    # Skip PostGIS or other extension tables if present
    if type_ == "table" and name in []:
        return False
    return True


def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """
    Enable accurate type comparison during autogenerate.
    Returns True to indicate a detected change should be included.
    """
    return None  # Let Alembic use default comparison


def process_revision_directives(context, revision, directives):
    """
    Hook to prevent generating empty migration files.
    If autogenerate detects no changes, it will not create a useless file.
    """
    if config.cmd_opts and getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            print("  No schema changes detected. Empty migration skipped.")


# ─── Offline Migration ────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Run migrations without an active DB connection.
    Outputs raw SQL to stdout — useful for review or manual execution.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


# ─── Online Migration ─────────────────────────────────────────────────────────

def run_migrations_online() -> None:
    """
    Run migrations with an active DB connection.
    This is the standard mode used in production and development.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Use NullPool for migrations — no connection reuse needed
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
            process_revision_directives=process_revision_directives,
            # Render item-level diffs for cleaner migration files
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()