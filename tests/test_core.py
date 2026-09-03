from pathlib import Path

from agent.config import Settings
from agent.core import MatAiasuAgent
from agent.memory.store import MemoryStore
from agent.models import Project
from agent.projects import ProjectRegistry


def test_agent_creates_plan(tmp_path: Path) -> None:
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.inspect("prepare the project")
    assert result.task.status.value == "done"
    assert len(result.task.steps) >= 4


def test_memory_roundtrip(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path)
    store.add("MatAiasu 3D uses Anycubic Next", kind="project-note")
    assert store.search("Anycubic")


def test_project_registry(tmp_path: Path) -> None:
    registry = ProjectRegistry(tmp_path)
    registry.add(Project("Demo", "/workspace/demo"))
    assert registry.list()[0].name == "Demo"


def test_readonly_execution(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')", encoding="utf-8")
    agent = MatAiasuAgent(Settings(data_dir=tmp_path / "data"))
    result = agent.execute_readonly("inspect workspace", tmp_path)
    assert result.task.status.value == "done"
    assert "1 files" in result.task.result
