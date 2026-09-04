from pathlib import Path

from agent.orchestrator import AgentOrchestrator
from agent.permissions import Permission, PermissionManager
from agent.tools.registry import ToolRegistry


class FakeModel:
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)

    def chat(self, prompt: str, system: str | None = None) -> str:
        return next(self.responses)


def test_orchestrator_executes_registered_read_tool(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')", encoding="utf-8")
    permissions = PermissionManager({Permission.READ_FILES})
    tools = ToolRegistry(permissions=permissions)
    model = FakeModel([
        '{"type":"tool_call","tool":"scan_workspace","args":{"cwd":"."}}',
        '{"type":"final","message":"Workspace inspected successfully."}',
    ])
    result = AgentOrchestrator(model, tools, permissions).run("inspect the project", tmp_path)
    assert result.stopped == "completed"
    assert result.tool_calls == 1
    assert result.message == "Workspace inspected successfully."


def test_orchestrator_stops_on_invalid_model_output(tmp_path: Path) -> None:
    permissions = PermissionManager({Permission.READ_FILES})
    tools = ToolRegistry(permissions=permissions)
    model = FakeModel(["not json"])
    result = AgentOrchestrator(model, tools, permissions).run("inspect", tmp_path)
    assert result.stopped == "invalid_model_output"
    assert result.tool_calls == 0


def test_orchestrator_cannot_bypass_write_permission(tmp_path: Path) -> None:
    permissions = PermissionManager({Permission.READ_FILES})
    tools = ToolRegistry(permissions=permissions)
    model = FakeModel([
        '{"type":"tool_call","tool":"write_file","args":{"path":"blocked.txt","content":"x"}}',
        '{"type":"final","message":"Stopped."}',
    ])
    result = AgentOrchestrator(model, tools, permissions).run("write a file", tmp_path)
    assert not (tmp_path / "blocked.txt").exists()
    assert result.tool_calls == 1
    assert any(event["type"] == "tool.failed" for event in result.events)
