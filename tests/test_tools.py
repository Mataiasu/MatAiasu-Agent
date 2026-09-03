from pathlib import Path

import pytest

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.permissions import Permission
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
