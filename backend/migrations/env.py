import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import app.models  # noqa: F401  autogenerate only sees models imported here
from app.config import get_settings
from app.database import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
target_metadata = Base.metadata
# SQLite cannot ALTER most column properties in place, so Alembic has to
# rebuild the table; only the local fallback needs this.
render_as_batch = settings.db_type == "sqlite"


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=render_as_batch,
        transaction_per_migration=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connect_args = {}
    if settings.db_type == "postgres":
        # Fail fast instead of queueing behind a long query: a waiting
        # ACCESS EXCLUSIVE lock blocks every later read on the table too.
        connect_args["options"] = "-c lock_timeout=5s -c statement_timeout=240s"
    engine = create_engine(settings.database_url, connect_args=connect_args)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=render_as_batch,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if settings.database_url is None:
    print("DB_ENABLED is false: nothing to migrate", file=sys.stderr)
elif context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
