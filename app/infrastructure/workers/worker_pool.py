import logging
import threading
from collections.abc import Callable
from queue import Empty, Queue

from app.domain.commands.text_work_command import TextWorkCommand

logger = logging.getLogger(__name__)


class WorkerPool:
    """Pool de hilos consumidores de la cola de textos."""

    def __init__(
        self,
        n_workers: int,
        work_queue: Queue[TextWorkCommand],
        process_one: Callable[[TextWorkCommand], None],
    ) -> None:
        self._n_workers = n_workers
        self._queue = work_queue
        self._process_one = process_one
        self._shutdown = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        for i in range(self._n_workers):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"text-worker-{i}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        logger.info("WorkerPool iniciado con %s workers.", self._n_workers)

    def _worker_loop(self) -> None:
        while not self._shutdown.is_set():
            try:
                cmd = self._queue.get(timeout=0.35)
            except Empty:
                continue
            try:
                self._process_one(cmd)
            except Exception:
                logger.exception("Error en worker procesando job=%s text=%s", cmd.job_id, cmd.text_id)
            finally:
                self._queue.task_done()

    def stop(self, join_timeout: float = 3.0) -> None:
        self._shutdown.set()
        for t in self._threads:
            t.join(timeout=join_timeout)
        logger.info("WorkerPool detenido.")
