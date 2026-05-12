from typing import Protocol

from app.domain.read_models.job_queries import JobTextResultView, OwnedJobView, SentimentReportView


class JobQueryRepository(Protocol):
    def get_owned_job(self, job_id: int, user_id: int) -> OwnedJobView | None: ...

    def count_texts_owned(self, job_id: int, user_id: int) -> int: ...

    def list_texts_page(
        self, job_id: int, user_id: int, offset: int, limit: int
    ) -> list[JobTextResultView]: ...

    def aggregate_sentiment_report_owned(self, job_id: int, user_id: int) -> SentimentReportView | None: ...
