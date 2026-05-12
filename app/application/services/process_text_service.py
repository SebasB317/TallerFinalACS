import logging
import random
import time

from app.application.analysis_config import AnalysisRuntimeConfig
from app.domain.commands.text_work_command import TextWorkCommand
from app.domain.ports.job_repository import JobRepository
from app.domain.sentiment import analyze_text_sentiment

logger = logging.getLogger(__name__)


class ProcessTextService:
    """Consumidor: simulación CPU-bound + análisis de sentimiento (Historia #3)."""

    def __init__(
        self,
        jobs: JobRepository,
        analysis: AnalysisRuntimeConfig,
        rng: random.Random | None = None,
    ) -> None:
        self._jobs = jobs
        self._analysis = analysis
        self._rng = rng or random.Random()

    def process_command(self, cmd: TextWorkCommand) -> None:
        job_id = self._jobs.mark_text_processing(cmd.text_id)
        if job_id is None:
            return
        self._jobs.mark_job_processing_if_pending(job_id)
        try:
            self._simulate_cpu_work()
            sentiment, score = analyze_text_sentiment(cmd.content)
            if not self._jobs.complete_text_with_result(cmd.text_id, sentiment.value, score):
                logger.warning("No se pudo completar text_id=%s (idempotencia)", cmd.text_id)
        except TimeoutError:
            logger.warning("Timeout simulado en análisis text_id=%s", cmd.text_id)
            if not self._jobs.mark_text_failed(cmd.text_id):
                logger.warning("No se pudo marcar failed text_id=%s", cmd.text_id)
        except Exception:
            logger.exception("Error analizando text_id=%s job_id=%s", cmd.text_id, job_id)
            if not self._jobs.mark_text_failed(cmd.text_id):
                logger.warning("No se pudo marcar failed text_id=%s", cmd.text_id)

    def _simulate_cpu_work(self) -> None:
        lo, hi = self._analysis.analysis_sleep_min_sec, self._analysis.analysis_sleep_max_sec
        if hi > 0:
            a, b = (lo, hi) if lo <= hi else (hi, lo)
            time.sleep(self._rng.uniform(a, b))
        p = self._analysis.simulated_analysis_timeout_probability
        if p > 0 and self._rng.random() < p:
            raise TimeoutError("timeout simulado del análisis")
