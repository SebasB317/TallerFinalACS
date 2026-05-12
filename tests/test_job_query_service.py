from unittest.mock import MagicMock

import pytest

from app.application.report_cache import get_cached_sentiment_report
from app.application.services.job_query_service import JobQueryService
from app.domain.exceptions import JobNotFoundError, JobNotReadyForReportError
from app.domain.job_status import JobStatus
from app.domain.read_models.job_queries import JobTextResultView, OwnedJobView, SentimentReportView


@pytest.fixture(autouse=True)
def _clear_report_cache() -> None:
    get_cached_sentiment_report.cache_clear()
    yield
    get_cached_sentiment_report.cache_clear()


def test_get_job_status_found() -> None:
    q = MagicMock()
    q.get_owned_job.return_value = OwnedJobView(1, 9, JobStatus.COMPLETED.value, 3, 3)
    r = JobQueryService(q).get_job_status(1, 9)
    assert r.job_id == 1
    assert r.processed_texts == 3


def test_get_job_status_not_found() -> None:
    q = MagicMock()
    q.get_owned_job.return_value = None
    with pytest.raises(JobNotFoundError):
        JobQueryService(q).get_job_status(1, 9)


def test_get_report_not_ready() -> None:
    q = MagicMock()
    q.get_owned_job.return_value = OwnedJobView(1, 9, JobStatus.PROCESSING.value, 5, 2)
    with pytest.raises(JobNotReadyForReportError):
        JobQueryService(q).get_report(1, 9)


def test_get_report_completed_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    q = MagicMock()
    q.get_owned_job.return_value = OwnedJobView(1, 9, JobStatus.COMPLETED.value, 2, 2)
    calls = {"n": 0}

    def fake_cache(uid: int, jid: int) -> tuple[int, int, int, float]:
        calls["n"] += 1
        return (2, 0, 0, 0.5)

    monkeypatch.setattr(
        "app.application.services.job_query_service.get_cached_sentiment_report",
        fake_cache,
    )
    r = JobQueryService(q).get_report(1, 9)
    assert r.positive_count == 2
    assert r.average_score == 0.5
    assert calls["n"] == 1


def test_list_results() -> None:
    q = MagicMock()
    q.get_owned_job.return_value = OwnedJobView(3, 1, JobStatus.COMPLETED.value, 2, 2)
    q.count_texts_owned.return_value = 2
    q.list_texts_page.return_value = [
        JobTextResultView(10, 0, "a", "completed", "NEUTRAL", 0.0),
        JobTextResultView(11, 1, "b", "completed", "POSITIVE", 0.8),
    ]
    total, items = JobQueryService(q).list_results(3, 1, page=1, per_page=20)
    assert total == 2
    assert len(items) == 2
    q.list_texts_page.assert_called_once_with(3, 1, 0, 20)
