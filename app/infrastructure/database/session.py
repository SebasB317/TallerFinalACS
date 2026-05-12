from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import JobModel, JobTextModel, UserModel  # noqa: F401

_engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _migrate_sqlite_job_counters() -> None:
    if not str(_engine.url).startswith("sqlite"):
        return
    insp = inspect(_engine)
    if "jobs" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("jobs")}
    added = False
    with _engine.begin() as conn:
        if "total_texts" not in cols:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN total_texts INTEGER NOT NULL DEFAULT 0"))
            added = True
        if "processed_texts" not in cols:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN processed_texts INTEGER NOT NULL DEFAULT 0"))
            added = True
        if added:
            conn.execute(
                text("""
                UPDATE jobs SET total_texts = (
                    SELECT COUNT(*) FROM job_texts jt WHERE jt.job_id = jobs.id
                )
                """)
            )
            conn.execute(
                text("""
                UPDATE jobs SET processed_texts = (
                    SELECT COUNT(*) FROM job_texts jt
                    WHERE jt.job_id = jobs.id AND jt.status IN ('completed', 'failed')
                )
                """)
            )


def init_db() -> None:
    Base.metadata.create_all(bind=_engine)
    _migrate_sqlite_job_counters()


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
