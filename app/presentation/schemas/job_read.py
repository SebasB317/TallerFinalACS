from pydantic import BaseModel, ConfigDict, Field


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    total_texts: int
    processed_texts: int


class JobTextItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    content: str
    status: str
    sentiment: str | None
    score: float | None


class JobResultsPageResponse(BaseModel):
    job_id: int
    page: int
    per_page: int
    total: int
    items: list[JobTextItemResponse]


class SentimentReportResponse(BaseModel):
    positive_count: int
    negative_count: int
    neutral_count: int
    average_score: float = Field(..., description="Promedio de score en textos completados (-1..1)")
