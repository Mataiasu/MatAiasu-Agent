from pathlib import Path

import pytest

from agent.executor import AgentExecutor
from agent.permissions import Permission, PermissionManager


def test_write_requires_permission(tmp_path: Path) -> None:
    executor = AgentExecutor(PermissionManager())
    with pytest.raises(PermissionError):
        executor.write_file(tmp_path / "blocked.txt", "no")


def test_write_allowed_with_permission(tmp_path: Path) -> None:
    permissions = PermissionManager({Permission.READ_FILES, Permission.WRITE_FILES})
    executor = AgentExecutor(permissions)
    target = tmp_path / "allowed.txt"
    executor.write_file(target, "yes")
    assert target.read_text(encoding="utf-8") == "yes"


def test_command_requires_permission(tmp_path: Path) -> None:
    executor = AgentExecutor(PermissionManager())
    with pytest.raises(PermissionError):
        executor.run_command(["python", "-c", "print(1)"], tmp_path)
