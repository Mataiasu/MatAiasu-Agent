from pathlib import Path

import pytest

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.permissions import Permission, PermissionManager
from agent.tools.git import GitTool
from agent.tools.registry import ToolRegistry


def test_git_tools_are_blocked_by_default(tmp_path: Path) -> None:
    registry = ToolRegistry()
    with pytest.raises(PermissionError):
        registry.resolve("git_status")


def test_git_permission_is_explicit(tmp_path: Path) -> None:
    registry = ToolRegistry(permissions=PermissionManager({Permission.READ_FILES, Permission.GIT}))
    for name in ("git_status", "git_diff", "git_root", "git_head"):
        handler = registry.resolve(name)
        assert callable(handler)


def test_agent_wires_git_permission(tmp_path: Path) -> None:
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data", allow_git=True))
    assert agent.permissions.allows(Permission.GIT)
    assert any(tool["name"] == "git_diff" for tool in agent.available_tools())


def test_git_head_returns_commit(tmp_path: Path) -> None:
    tool = GitTool()
    code, stdout, stderr = tool.head(tmp_path)
    assert code != 0
    assert stderr or stdout
