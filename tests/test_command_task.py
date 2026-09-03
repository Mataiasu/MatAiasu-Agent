from pathlib import Path

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.models import TaskStatus


def test_command_task_is_blocked_without_permission(tmp_path: Path) -> None:
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.execute_command_task("run test", ["python", "-c", "print(1)"], tmp_path)
    assert result.task.status == TaskStatus.BLOCKED


def test_command_task_runs_when_explicitly_enabled(tmp_path: Path) -> None:
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data", allow_commands=True))
    result = agent.execute_command_task("run test", ["python", "-c", "print(1)"], tmp_path)
    assert result.task.status == TaskStatus.DONE
    assert "1" in result.task.result
