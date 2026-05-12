import logging

from app.application.analysis_config import AnalysisRuntimeConfig
from app.application.services.process_text_service import ProcessTextService
from app.domain.commands.text_work_command import TextWorkCommand
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.job_repository_sqlalchemy import SqlAlchemyJobRepository

logger = logging.getLogger(__name__)

_analysis_cfg: AnalysisRuntimeConfig = AnalysisRuntimeConfig(
    analysis_sleep_min_sec=0.045,
    analysis_sleep_max_sec=0.055,
    simulated_analysis_timeout_probability=0.0,
)


def configure_worker_analysis(cfg: AnalysisRuntimeConfig) -> None:
    global _analysis_cfg
    _analysis_cfg = cfg


def process_text_job(cmd: TextWorkCommand) -> None:
    """Unidad de trabajo ejecutada por cada worker (nueva sesión por ítem)."""
    db = SessionLocal()
    try:
        repo = SqlAlchemyJobRepository(db)
        ProcessTextService(repo, _analysis_cfg).process_command(cmd)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Fallo transaccional job=%s text=%s", cmd.job_id, cmd.text_id)
        raise
    finally:
        db.close()
