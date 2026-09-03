from pathlib import Path

from agent.planner import TaskPlanner
from agent.validator import Validator


def test_planner_builds_safe_plan() -> None:
    plan = TaskPlanner().build("fix the project")
    assert plan.objective == "fix the project"
    assert "Check required permissions" in plan.steps


def test_validator_accepts_workspace(tmp_path: Path) -> None:
    (tmp_path / "file.txt").write_text("ok", encoding="utf-8")
    result = Validator().workspace(tmp_path)
    assert result.ok


def test_validator_rejects_failed_command() -> None:
    result = Validator().command(1, "", "boom")
    assert not result.ok
    assert result.message == "boom"
