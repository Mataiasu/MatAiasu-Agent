from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .history import HistoryStore
from .ollama import OllamaClient
from .permissions import PermissionManager
from .tools.policy import WorkspacePolicy
from .tools.registry import ToolRegistry


@dataclass(slots=True)
class OrchestrationResult:
    message: str
    turns: int
    tool_calls: int
    events: list[dict[str, Any]]
    stopped: str = "completed"


class AgentOrchestrator:
    """Bounded model/tool loop. Model output never bypasses the tool registry."""

    def __init__(
        self,
        model: OllamaClient,
        tools: ToolRegistry,
        permissions: PermissionManager,
        history: HistoryStore | None = None,
        max_turns: int = 12,
        max_tool_calls: int = 30,
    ) -> None:
        self.model = model
        self.tools = tools
        self.permissions = permissions
        self.history = history
        self.max_turns = max(1, max_turns)
        self.max_tool_calls = max(1, max_tool_calls)

    def _record(self, event_type: str, data: dict[str, Any]) -> None:
        if self.history is not None:
            self.history.append(event_type, data)

    def _parse(self, response: str) -> dict[str, Any]:
        text = response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Model must return a single JSON object") from exc
        if not isinstance(data, dict) or data.get("type") not in {"tool_call", "final"}:
            raise ValueError("Invalid agent response type")
        return data

    def _safe_args(self, name: str, args: dict[str, Any], policy: WorkspacePolicy) -> dict[str, Any]:
        if not isinstance(args, dict):
            raise ValueError("Tool args must be an object")
        args = dict(args)
        if name in {"read_file", "write_file"}:
            if "path" not in args:
                raise ValueError("path is required")
            args["path"] = str(policy.resolve(Path(str(args["path"]))))
        elif name in {"scan_workspace", "git_status", "git_diff", "git_root", "git_head", "git_branches", "git_remote", "git_fetch", "git_pull", "git_push"}:
            cwd = Path(str(args.pop("cwd", policy.root)))
            resolved = policy.resolve(cwd)
            if name.startswith("git_") and not (resolved / ".git").exists():
                if not (resolved / ".git").is_file():
                    raise ValueError("cwd is not a Git repository")
            args["cwd"] = str(resolved)
        elif name == "run_command":
            command = args.get("command")
            if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                raise ValueError("command must be a non-empty string list")
            cwd = policy.resolve(Path(str(args.get("cwd", policy.root))))
            args["command"] = command
            args["cwd"] = str(cwd)
        elif name == "git_add":
            cwd = policy.resolve(Path(str(args.pop("cwd", policy.root))))
            paths = args.get("paths")
            if not isinstance(paths, list) or not paths or not all(isinstance(x, str) and x for x in paths):
                raise ValueError("paths must be a non-empty string list")
            for path in paths:
                policy.resolve(cwd / path)
            args["cwd"] = str(cwd)
        elif name == "git_commit":
            cwd = policy.resolve(Path(str(args.pop("cwd", policy.root))))
            message = args.get("message")
            if not isinstance(message, str) or not message.strip():
                raise ValueError("commit message is required")
            args["cwd"] = str(cwd)
            args["message"] = message.strip()
        elif name == "git_log":
            args["cwd"] = str(policy.resolve(Path(str(args.get("cwd", policy.root)))))
        else:
            raise ValueError(f"Unsupported tool: {name}")
        return args

    def run(self, objective: str, workspace: str | Path) -> OrchestrationResult:
        objective = objective.strip()
        if not objective:
            raise ValueError("Objective cannot be empty")
        policy = WorkspacePolicy(Path(workspace))
        tool_description = json.dumps(self.tools.describe(), ensure_ascii=False)
        system = (
            "You are MatAiasu Agent. Work only inside the supplied workspace. "
            "Return exactly one JSON object and no markdown. For an action use "
            '{"type":"tool_call","tool":"NAME","args":{...}}. '
            'When finished use {"type":"final","message":"..."}. '
            "Use the smallest safe action. Inspect before modifying. Never claim an action succeeded unless its tool result says so. "
            f"Available tools: {tool_description}"
        )
        prompt = f"Workspace: {policy.root}\nObjective: {objective}\nBegin by inspecting the project."
        events: list[dict[str, Any]] = []
        tool_calls = 0
        self._record("orchestration.started", {"objective": objective, "workspace": str(policy.root)})
        for turn in range(1, self.max_turns + 1):
            response = self.model.chat(prompt, system=system)
            try:
                action = self._parse(response)
            except ValueError as exc:
                event = {"type": "model.invalid", "error": str(exc), "turn": turn}
                events.append(event)
                self._record("orchestration.event", event)
                return OrchestrationResult("Model returned an invalid action; execution stopped safely.", turn, tool_calls, events, "invalid_model_output")
            if action["type"] == "final":
                message = str(action.get("message", "")).strip()
                event = {"type": "agent.final", "message": message, "turn": turn}
                events.append(event)
                self._record("orchestration.event", event)
                return OrchestrationResult(message, turn, tool_calls, events)
            if tool_calls >= self.max_tool_calls:
                event = {"type": "agent.limit", "limit": self.max_tool_calls}
                events.append(event)
                self._record("orchestration.event", event)
                return OrchestrationResult("Tool-call limit reached; execution stopped safely.", turn, tool_calls, events, "tool_limit")
            name = action.get("tool")
            if not isinstance(name, str) or not name:
                event = {"type": "agent.invalid_tool", "turn": turn}
                events.append(event)
                self._record("orchestration.event", event)
                return OrchestrationResult("Missing tool name; execution stopped safely.", turn, tool_calls, events, "invalid_tool")
            try:
                args = self._safe_args(name, action.get("args", {}), policy)
                result = self.tools.resolve(name)(**args)
                tool_calls += 1
                event = {"type": "tool.executed", "tool": name, "turn": turn}
                events.append(event)
                self._record("orchestration.event", event)
                serialized = json.dumps(result, ensure_ascii=False, default=str)
                prompt = f"Previous tool: {name}\nResult: {serialized}\nContinue the objective."
            except Exception as exc:
                tool_calls += 1
                event = {"type": "tool.failed", "tool": name, "turn": turn, "error": str(exc)}
                events.append(event)
                self._record("orchestration.event", event)
                prompt = f"Previous tool: {name}\nTool failed with: {exc}\nAnalyze the failure and continue safely."
        event = {"type": "agent.limit", "limit": self.max_turns}
        events.append(event)
        self._record("orchestration.event", event)
        return OrchestrationResult("Turn limit reached; execution stopped safely.", self.max_turns, tool_calls, events, "turn_limit")
