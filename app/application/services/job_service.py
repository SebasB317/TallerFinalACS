from app.domain.commands.text_work_command import TextWorkCommand
from app.domain.constants import MAX_TEXTS_PER_JOB
from app.domain.exceptions import EmptyJobBatchError, TooManyTextsInBatchError
from app.domain.ports.job_repository import JobRepository
from app.domain.ports.text_work_queue import TextWorkQueuePort


class JobService:
    """Crea trabajos en BD y publica comandos en la cola (después de commit, ver router)."""

    def __init__(
        self,
        jobs: JobRepository,
        queue: TextWorkQueuePort,
        max_texts_per_job: int = MAX_TEXTS_PER_JOB,
    ) -> None:
        self._jobs = jobs
        self._queue = queue
        self._max = max_texts_per_job

    def persist_new_job(self, user_id: int, texts: list[str]) -> tuple[int, list[TextWorkCommand]]:
        if not texts:
            raise EmptyJobBatchError("Debe enviar al menos un texto.")
        if len(texts) > self._max:
            raise TooManyTextsInBatchError(f"Máximo {self._max} textos por lote.")
        job_id, text_ids = self._jobs.create_job_with_texts(user_id, texts)
        cmds = [
            TextWorkCommand(job_id=job_id, text_id=tid, user_id=user_id, content=txt)
            for tid, txt in zip(text_ids, texts, strict=True)
        ]
        return job_id, cmds

    def publish_commands(self, cmds: list[TextWorkCommand]) -> None:
        for c in cmds:
            self._queue.put(c)
