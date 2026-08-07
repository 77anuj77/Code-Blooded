import os
from pathlib import Path

from sqlmodel import SQLModel, create_engine

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def get_engine():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. Cannot connect to Supabase."
        )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 3,
        },
    )


def init_db():
    from ingest import models  # noqa: F401 — registers all table metadata

    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    return engine
