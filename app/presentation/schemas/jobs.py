from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100)


class CreateJobResponse(BaseModel):
    job_id: int
    status: str
