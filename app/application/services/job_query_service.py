from app.application.report_cache import get_cached_sentiment_report
from app.domain.exceptions import JobNotFoundError, JobNotReadyForReportError
from app.domain.job_status import JobStatus
from app.domain.ports.job_query_repository import JobQueryRepository
from app.domain.read_models.job_queries import JobTextResultView, OwnedJobView, SentimentReportView


class JobQueryService:
    def __init__(self, queries: JobQueryRepository) -> None:
        self._q = queries

    def get_job_status(self, job_id: int, user_id: int) -> OwnedJobView:
        row = self._q.get_owned_job(job_id, user_id)
        if row is None:
            raise JobNotFoundError("Trabajo no encontrado.")
        return row

    def list_results(
        self, job_id: int, user_id: int, page: int, per_page: int
    ) -> tuple[int, list[JobTextResultView]]:
        self.get_job_status(job_id, user_id)
        total = self._q.count_texts_owned(job_id, user_id)
        offset = (page - 1) * per_page
        items = self._q.list_texts_page(job_id, user_id, offset, per_page)
        return total, items

    def get_report(self, job_id: int, user_id: int) -> SentimentReportView:
        job = self.get_job_status(job_id, user_id)
        if job.status != JobStatus.COMPLETED.value:
            raise JobNotReadyForReportError("El trabajo aún no está completado.")
        pos, neg, neu, avg = get_cached_sentiment_report(user_id, job_id)
        return SentimentReportView(
            positive_count=pos,
            negative_count=neg,
            neutral_count=neu,
            average_score=avg,
        )
