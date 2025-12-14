from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from pathlib import Path

# This is the key fix: add the backend directory to Python path
CURRENT_DIR = Path(__file__).resolve().parent.parent  # backend/
if str(CURRENT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(CURRENT_DIR))

# Load environment variables from .env in backend/
from dotenv import load_dotenv
load_dotenv(dotenv_path=CURRENT_DIR / ".env")

# Now we can safely import app
from app.models import Base  # This will now work

# this is the Alembic Config object
config = context.config

# Set the SQLAlchemy URL from .env
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()