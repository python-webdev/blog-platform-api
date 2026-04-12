# pyright: reportAttributeAccessIssue=false
# mypy: ignore-errors
# pylint: disable=no-member

import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.config import settings
from app.models import Base  # noqa: F401 - imports all models

config = getattr(context, "config")
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    getattr(context, "configure")(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with getattr(context, "begin_transaction")():
        getattr(context, "run_migrations")()


def do_run_migrations(connection: Connection) -> None:
    getattr(context, "configure")(
        connection=connection,
        target_metadata=target_metadata,
    )
    with getattr(context, "begin_transaction")():
        getattr(context, "run_migrations")()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if getattr(context, "is_offline_mode")():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
