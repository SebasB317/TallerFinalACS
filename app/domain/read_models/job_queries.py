from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OwnedJobView:
    job_id: int
    user_id: int
    status: str
    total_texts: int
    processed_texts: int


@dataclass(frozen=True, slots=True)
class JobTextResultView:
    id: int
    position: int
    content: str
    status: str
    sentiment: str | None
    score: float | None


@dataclass(frozen=True, slots=True)
class SentimentReportView:
    positive_count: int
    negative_count: int
    neutral_count: int
    average_score: float
