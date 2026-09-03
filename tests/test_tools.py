from pathlib import Path

import pytest

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.permissions import Permission, PermissionManager
from agent.tools.git import GitTool
from agent.tools.policy import WorkspacePolicy
from agent.tools.registry import ToolRegistry


def test_tool_registry_rejects_unknown_tool() -> None:
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("delete_everything")


def test_tool_registry_exposes_permissioned_tools() -> None:
    registry = ToolRegistry()
    tools = {item["name"]: item["permission"] for item in registry.describe()}
    assert tools["read_file"] == Permission.READ_FILES.value
    assert tools["write_file"] == Permission.WRITE_FILES.value
    assert tools["run_command"] == Permission.RUN_COMMANDS.value
    assert tools["git_status"] == Permission.GIT.value
    assert tools["git_head"] == Permission.GIT.value


def test_tool_registry_blocks_git_by_default() -> None:
    registry = ToolRegistry()
    with pytest.raises(PermissionError):
        registry.resolve("git_head")


def test_git_head_is_available_with_git_permission(tmp_path: Path) -> None:
    registry = ToolRegistry(permissions=PermissionManager({Permission.GIT}))
    handler = registry.resolve("git_head")
    assert callable(handler)


def test_empty_permission_set_grants_nothing() -> None:
    permissions = PermissionManager(set())
    assert not permissions.allows(Permission.READ_FILES)
    with pytest.raises(PermissionError):
        permissions.require(Permission.READ_FILES)


def test_workspace_policy_blocks_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    policy = WorkspacePolicy(workspace)
    with pytest.raises(PermissionError):
        policy.resolve(tmp_path / "outside.txt")


def test_project_detection(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.detect_project(tmp_path)
    assert result["primary_type"] == "godot"
    assert set(result["types"]) == {"godot", "node"}
