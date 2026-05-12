from sqlalchemy import case, func, select, update
from sqlalchemy.orm import Session

from app.domain.job_status import JobStatus, JobTextStatus
from app.domain.ports.job_repository import JobRepository
from app.domain.read_models.job_queries import JobTextResultView, OwnedJobView, SentimentReportView
from app.infrastructure.database.models import JobModel, JobTextModel


class SqlAlchemyJobRepository(JobRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_job_with_texts(self, user_id: int, texts: list[str]) -> tuple[int, list[int]]:
        n = len(texts)
        job = JobModel(
            user_id=user_id,
            status=JobStatus.PENDING.value,
            total_texts=n,
            processed_texts=0,
        )
        self._session.add(job)
        self._session.flush()
        for pos, content in enumerate(texts):
            row = JobTextModel(
                job_id=job.id,
                content=content,
                position=pos,
                status=JobTextStatus.PENDING.value,
            )
            self._session.add(row)
        self._session.flush()
        ids = self._session.scalars(
            select(JobTextModel.id).where(JobTextModel.job_id == job.id).order_by(JobTextModel.position)
        ).all()
        return job.id, list(ids)

    def mark_job_processing_if_pending(self, job_id: int) -> None:
        j = self._session.get(JobModel, job_id)
        if j is not None and j.status == JobStatus.PENDING.value:
            j.status = JobStatus.PROCESSING.value

    def mark_text_processing(self, text_id: int) -> int | None:
        row = self._session.get(JobTextModel, text_id)
        if row is None or row.status != JobTextStatus.PENDING.value:
            return None
        row.status = JobTextStatus.PROCESSING.value
        return row.job_id

    def complete_text_with_result(self, text_id: int, sentiment: str, score: float) -> bool:
        res = self._session.execute(
            update(JobTextModel)
            .where(
                JobTextModel.id == text_id,
                JobTextModel.status == JobTextStatus.PROCESSING.value,
            )
            .values(
                sentiment=sentiment,
                score=score,
                status=JobTextStatus.COMPLETED.value,
            )
            .returning(JobTextModel.job_id)
        )
        row = res.first()
        if row is None:
            return False
        self._bump_job_progress(int(row[0]))
        return True

    def mark_text_failed(self, text_id: int) -> bool:
        res = self._session.execute(
            update(JobTextModel)
            .where(
                JobTextModel.id == text_id,
                JobTextModel.status == JobTextStatus.PROCESSING.value,
            )
            .values(status=JobTextStatus.FAILED.value)
            .returning(JobTextModel.job_id)
        )
        row = res.first()
        if row is None:
            return False
        self._bump_job_progress(int(row[0]))
        return True

    def _bump_job_progress(self, job_id: int) -> None:
        self._session.execute(
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(processed_texts=JobModel.processed_texts + 1)
        )
        job = self._session.get(JobModel, job_id)
        if job is None:
            return
        self._session.refresh(job)
        if job.total_texts > 0 and job.processed_texts >= job.total_texts:
            job.status = JobStatus.COMPLETED.value

    def get_owned_job(self, job_id: int, user_id: int) -> OwnedJobView | None:
        row = self._session.scalar(
            select(JobModel).where(JobModel.id == job_id, JobModel.user_id == user_id)
        )
        if row is None:
            return None
        return OwnedJobView(
            job_id=row.id,
            user_id=row.user_id,
            status=row.status,
            total_texts=row.total_texts,
            processed_texts=row.processed_texts,
        )

    def count_texts_owned(self, job_id: int, user_id: int) -> int:
        n = self._session.scalar(
            select(func.count())
            .select_from(JobTextModel)
            .join(JobModel, JobTextModel.job_id == JobModel.id)
            .where(JobModel.id == job_id, JobModel.user_id == user_id)
        )
        return int(n or 0)

    def list_texts_page(
        self, job_id: int, user_id: int, offset: int, limit: int
    ) -> list[JobTextResultView]:
        rows = self._session.scalars(
            select(JobTextModel)
            .join(JobModel, JobTextModel.job_id == JobModel.id)
            .where(JobModel.id == job_id, JobModel.user_id == user_id)
            .order_by(JobTextModel.position)
            .offset(offset)
            .limit(limit)
        ).all()
        return [
            JobTextResultView(
                id=r.id,
                position=r.position,
                content=r.content,
                status=r.status,
                sentiment=r.sentiment,
                score=r.score,
            )
            for r in rows
        ]

    def aggregate_sentiment_report_owned(self, job_id: int, user_id: int) -> SentimentReportView | None:
        if self.get_owned_job(job_id, user_id) is None:
            return None
        pos = func.coalesce(
            func.sum(case((JobTextModel.sentiment == "POSITIVE", 1), else_=0)),
            0,
        )
        neg = func.coalesce(
            func.sum(case((JobTextModel.sentiment == "NEGATIVE", 1), else_=0)),
            0,
        )
        neu = func.coalesce(
            func.sum(case((JobTextModel.sentiment == "NEUTRAL", 1), else_=0)),
            0,
        )
        avg_score = func.coalesce(func.avg(JobTextModel.score), 0.0)
        stmt = (
            select(pos, neg, neu, avg_score)
            .select_from(JobTextModel)
            .join(JobModel, JobTextModel.job_id == JobModel.id)
            .where(
                JobModel.id == job_id,
                JobModel.user_id == user_id,
                JobTextModel.status == JobTextStatus.COMPLETED.value,
                JobTextModel.sentiment.isnot(None),
            )
        )
        row = self._session.execute(stmt).one()
        return SentimentReportView(
            positive_count=int(row[0] or 0),
            negative_count=int(row[1] or 0),
            neutral_count=int(row[2] or 0),
            average_score=float(row[3] or 0.0),
        )
