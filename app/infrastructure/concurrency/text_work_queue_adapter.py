from queue import Queue

from app.domain.commands.text_work_command import TextWorkCommand
from app.domain.ports.text_work_queue import TextWorkQueuePort

_shared_queue: Queue[TextWorkCommand] | None = None


def get_shared_text_queue() -> Queue[TextWorkCommand]:
    global _shared_queue
    if _shared_queue is None:
        _shared_queue = Queue()
    return _shared_queue


class ThreadSafeTextWorkQueue(TextWorkQueuePort):
    """Adaptador `queue.Queue` (thread-safe) al puerto de dominio."""

    def __init__(self, backing: Queue[TextWorkCommand] | None = None) -> None:
        self._q = backing or get_shared_text_queue()

    def put(self, item: TextWorkCommand) -> None:
        self._q.put(item)
