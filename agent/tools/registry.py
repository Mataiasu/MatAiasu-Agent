from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..permissions import Permission
from .files import FileTool
from .shell import ShellTool
from .workspace import WorkspaceScanner


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    permission: Permission


class ToolRegistry:
    """Machine-readable allowlist for operations exposed to the agent."""

    def __init__(self, files: FileTool | None = None, shell: ShellTool | None = None) -> None:
        self.files = files or FileTool()
        self.shell = shell or ShellTool()
        self.scanner = WorkspaceScanner()
        self._specs = {
            "read_file": ToolSpec("read_file", "Read a UTF-8 text file", Permission.READ_FILES),
            "write_file": ToolSpec("write_file", "Write a UTF-8 text file", Permission.WRITE_FILES),
            "run_command": ToolSpec("run_command", "Run an explicit command", Permission.RUN_COMMANDS),
            "scan_workspace": ToolSpec("scan_workspace", "Inspect workspace files", Permission.READ_FILES),
        }

    def specs(self) -> tuple[ToolSpec, ...]:
        return tuple(self._specs.values())

    def get(self, name: str) -> ToolSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def resolve(self, name: str) -> Callable[..., object]:
        self.get(name)
        handlers: dict[str, Callable[..., object]] = {
            "read_file": self.files.read,
            "write_file": self.files.write,
            "run_command": self.shell.run,
            "scan_workspace": self.scanner.scan,
        }
        return handlers[name]

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": spec.name, "description": spec.description, "permission": spec.permission.value}
            for spec in self.specs()
        ]
