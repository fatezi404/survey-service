import os
import asyncio

from dotenv import load_dotenv
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.session import Base
from app.models import user_model
from app.models import role_model
from app.models import permission_model
from app.models import association_tables

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, echo=True, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
