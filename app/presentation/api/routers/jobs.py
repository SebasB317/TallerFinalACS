from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.services.job_query_service import JobQueryService
from app.application.services.job_service import JobService
from app.domain.entities.user import User
from app.domain.exceptions import (
    EmptyJobBatchError,
    JobNotFoundError,
    JobNotReadyForReportError,
    TooManyTextsInBatchError,
)
from app.presentation.deps import get_current_user, get_db, get_job_query_service, get_job_service
from app.presentation.schemas.job_read import (
    JobResultsPageResponse,
    JobStatusResponse,
    JobTextItemResponse,
    SentimentReportResponse,
)
from app.presentation.schemas.jobs import CreateJobRequest, CreateJobResponse

router = APIRouter(tags=["jobs"])


@router.post("/jobs", response_model=CreateJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
    body: CreateJobRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> CreateJobResponse:
    assert current.id is not None
    try:
        job_id, cmds = job_service.persist_new_job(current.id, body.texts)
        db.commit()
    except TooManyTextsInBatchError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except EmptyJobBatchError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except Exception:
        db.rollback()
        raise
    job_service.publish_commands(cmds)
    return CreateJobResponse(job_id=job_id, status="pending")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: int,
    current: User = Depends(get_current_user),
    svc: JobQueryService = Depends(get_job_query_service),
) -> JobStatusResponse:
    assert current.id is not None
    try:
        j = svc.get_job_status(job_id, current.id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return JobStatusResponse(
        job_id=j.job_id,
        status=j.status,
        total_texts=j.total_texts,
        processed_texts=j.processed_texts,
    )


@router.get("/jobs/{job_id}/results", response_model=JobResultsPageResponse)
def get_job_results(
    job_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current: User = Depends(get_current_user),
    svc: JobQueryService = Depends(get_job_query_service),
) -> JobResultsPageResponse:
    assert current.id is not None
    try:
        total, items = svc.list_results(job_id, current.id, page, per_page)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return JobResultsPageResponse(
        job_id=job_id,
        page=page,
        per_page=per_page,
        total=total,
        items=[
            JobTextItemResponse(
                id=i.id,
                position=i.position,
                content=i.content,
                status=i.status,
                sentiment=i.sentiment,
                score=i.score,
            )
            for i in items
        ],
    )


@router.get("/jobs/{job_id}/report", response_model=SentimentReportResponse)
def get_job_report(
    job_id: int,
    current: User = Depends(get_current_user),
    svc: JobQueryService = Depends(get_job_query_service),
) -> SentimentReportResponse:
    assert current.id is not None
    try:
        r = svc.get_report(job_id, current.id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except JobNotReadyForReportError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return SentimentReportResponse(
        positive_count=r.positive_count,
        negative_count=r.negative_count,
        neutral_count=r.neutral_count,
        average_score=r.average_score,
    )
