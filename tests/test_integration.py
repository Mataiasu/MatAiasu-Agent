from pathlib import Path

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.permissions import Permission


def test_readonly_end_to_end(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')", encoding="utf-8")
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.execute_readonly("inspect project", tmp_path)
    assert result.task.status.value == "done"
    assert result.task.result.startswith("Workspace valid:")
    assert agent.permissions.allows(Permission.READ_FILES)


def test_command_cycle_is_blocked_without_permission(tmp_path: Path) -> None:
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.execute_command_task("run test", ["python", "-c", "print(1)"], tmp_path)
    assert result.task.status.value == "blocked"
    assert "run_commands" in result.task.result
