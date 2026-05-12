from unittest.mock import MagicMock

from app.application.analysis_config import AnalysisRuntimeConfig
from app.application.services.process_text_service import ProcessTextService
from app.domain.commands.text_work_command import TextWorkCommand


def test_process_command_happy_path() -> None:
    repo = MagicMock()
    repo.mark_text_processing.return_value = 99
    cfg = AnalysisRuntimeConfig(0.0, 0.0, 0.0)
    svc = ProcessTextService(repo, cfg)
    cmd = TextWorkCommand(job_id=1, text_id=2, user_id=3, content="muy excelente")
    svc.process_command(cmd)
    repo.mark_text_processing.assert_called_once_with(2)
    repo.mark_job_processing_if_pending.assert_called_once_with(99)
    repo.complete_text_with_result.assert_called_once()
    args = repo.complete_text_with_result.call_args[0]
    assert args[0] == 2
    assert args[1] == "POSITIVE"
    assert isinstance(args[2], float)
    repo.mark_text_failed.assert_not_called()


def test_process_command_timeout_marks_failed() -> None:
    repo = MagicMock()
    repo.mark_text_processing.return_value = 99
    cfg = AnalysisRuntimeConfig(0.0, 0.0, 1.0)
    svc = ProcessTextService(repo, cfg)
    cmd = TextWorkCommand(job_id=1, text_id=2, user_id=3, content="x")
    svc.process_command(cmd)
    repo.complete_text_with_result.assert_not_called()
    repo.mark_text_failed.assert_called_once_with(2)


def test_process_command_skips_if_not_pending() -> None:
    repo = MagicMock()
    repo.mark_text_processing.return_value = None
    cfg = AnalysisRuntimeConfig(0.0, 0.0, 0.0)
    ProcessTextService(repo, cfg).process_command(
        TextWorkCommand(job_id=1, text_id=2, user_id=3, content="x")
    )
    repo.mark_job_processing_if_pending.assert_not_called()
