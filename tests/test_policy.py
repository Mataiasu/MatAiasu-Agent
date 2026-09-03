from pathlib import Path

import pytest

from agent.tools.policy import WorkspacePolicy


def test_policy_allows_relative_paths(tmp_path: Path) -> None:
    policy = WorkspacePolicy(tmp_path)
    assert policy.resolve(Path("src/main.py")) == tmp_path / "src/main.py"


def test_policy_blocks_paths_outside_workspace(tmp_path: Path) -> None:
    policy = WorkspacePolicy(tmp_path)
    with pytest.raises(PermissionError):
        policy.resolve(tmp_path.parent / "outside.txt")


def test_policy_accepts_workspace_cwd(tmp_path: Path) -> None:
    policy = WorkspacePolicy(tmp_path)
    assert policy.cwd(Path(".")) == tmp_path
