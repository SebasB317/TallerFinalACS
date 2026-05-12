from typing import Protocol

from app.domain.commands.text_work_command import TextWorkCommand


class TextWorkQueuePort(Protocol):
    def put(self, item: TextWorkCommand) -> None: ...
