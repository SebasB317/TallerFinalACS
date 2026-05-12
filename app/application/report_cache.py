from functools import lru_cache

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.job_repository_sqlalchemy import SqlAlchemyJobRepository


@lru_cache(maxsize=256)
def get_cached_sentiment_report(user_id: int, job_id: int) -> tuple[int, int, int, float]:
    """Caché LRU para reportes de trabajos `completed` (inmutables)."""
    db = SessionLocal()
    try:
        repo = SqlAlchemyJobRepository(db)
        r = repo.aggregate_sentiment_report_owned(job_id, user_id)
        if r is None:
            raise ValueError("sin trabajo")
        return (
            r.positive_count,
            r.negative_count,
            r.neutral_count,
            r.average_score,
        )
    finally:
        db.close()
