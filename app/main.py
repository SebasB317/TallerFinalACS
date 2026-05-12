from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.application.analysis_config import AnalysisRuntimeConfig
from app.config import settings
from app.infrastructure.concurrency.text_work_queue_adapter import get_shared_text_queue
from app.infrastructure.database.session import init_db
from app.infrastructure.workers.text_worker import configure_worker_analysis, process_text_job
from app.infrastructure.workers.worker_pool import WorkerPool
from app.presentation.api.routers import analysis, auth, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    configure_worker_analysis(AnalysisRuntimeConfig.from_settings(settings))
    queue = get_shared_text_queue()
    pool = WorkerPool(settings.worker_count, queue, process_text_job)
    pool.start()
    app.state.worker_pool = pool
    yield
    pool.stop()


app = FastAPI(title="Taller Final — Sistema de análisis", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(jobs.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
