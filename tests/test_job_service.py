from unittest.mock import MagicMock

import pytest

from app.application.services.job_service import JobService
from app.domain.commands.text_work_command import TextWorkCommand
from app.domain.exceptions import EmptyJobBatchError, TooManyTextsInBatchError


def test_persist_new_job_enqueues_commands_order() -> None:
    repo = MagicMock()
    repo.create_job_with_texts.return_value = (7, [10, 11, 12])
    q = MagicMock()
    svc = JobService(repo, q, max_texts_per_job=100)
    jid, cmds = svc.persist_new_job(1, ["a", "b", "c"])
    assert jid == 7
    assert len(cmds) == 3
    assert cmds[0] == TextWorkCommand(job_id=7, text_id=10, user_id=1, content="a")
    repo.create_job_with_texts.assert_called_once_with(1, ["a", "b", "c"])
    q.put.assert_not_called()


def test_publish_commands() -> None:
    repo = MagicMock()
    q = MagicMock()
    svc = JobService(repo, q)
    cmds = [TextWorkCommand(1, 2, 3, "x")]
    svc.publish_commands(cmds)
    q.put.assert_called_once_with(cmds[0])


def test_too_many_texts() -> None:
    repo = MagicMock()
    q = MagicMock()
    svc = JobService(repo, q, max_texts_per_job=2)
    with pytest.raises(TooManyTextsInBatchError):
        svc.persist_new_job(1, ["a", "b", "c"])


def test_empty_batch() -> None:
    repo = MagicMock()
    q = MagicMock()
    svc = JobService(repo, q)
    with pytest.raises(EmptyJobBatchError):
        svc.persist_new_job(1, [])
