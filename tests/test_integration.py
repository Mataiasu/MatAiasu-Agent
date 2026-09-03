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


def test_command_cycle_runs_with_explicit_permission(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "data", allow_commands=True)
    agent = MatAiasuAgent(settings)
    result = agent.execute_command_task("run smoke test", ["python", "-c", "print('ok')"], tmp_path)
    assert result.task.status.value == "done"
    assert result.task.result.startswith("Command succeeded")


def test_write_cycle_requires_and_uses_explicit_permission(tmp_path: Path) -> None:
    blocked = MatAiasuAgent(Settings(data_dir=tmp_path / "blocked"))
    target = tmp_path / "blocked" / "workspace" / "hello.txt"
    target.parent.mkdir(parents=True)
    try:
        blocked.write_file(target, "no")
    except PermissionError:
        pass
    else:
        raise AssertionError("write should require explicit permission")

    allowed = MatAiasuAgent(Settings(data_dir=tmp_path / "allowed", allow_write=True))
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    file_path = workspace / "hello.txt"
    allowed.write_file(file_path, "hello", workspace)
    assert file_path.read_text(encoding="utf-8") == "hello"
