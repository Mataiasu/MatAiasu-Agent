from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..permissions import Permission, PermissionManager
from .files import FileTool
from .git import GitTool
from .shell import ShellTool
from .workspace import WorkspaceScanner


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    permission: Permission


class ToolRegistry:
    """Machine-readable allowlist for operations exposed to the agent."""

    def __init__(self, files: FileTool | None = None, shell: ShellTool | None = None, git: GitTool | None = None, permissions: PermissionManager | None = None) -> None:
        self.files = files or FileTool()
        self.shell = shell or ShellTool()
        self.git = git or GitTool(self.shell)
        self.scanner = WorkspaceScanner()
        self.permissions = permissions or PermissionManager()
        self._specs = {
            "read_file": ToolSpec("read_file", "Read a UTF-8 text file", Permission.READ_FILES),
            "write_file": ToolSpec("write_file", "Write a UTF-8 text file", Permission.WRITE_FILES),
            "run_command": ToolSpec("run_command", "Run an explicit command", Permission.RUN_COMMANDS),
            "scan_workspace": ToolSpec("scan_workspace", "Inspect workspace files", Permission.READ_FILES),
            "git_status": ToolSpec("git_status", "Inspect Git working tree status", Permission.GIT),
            "git_diff": ToolSpec("git_diff", "Inspect Git diff", Permission.GIT),
            "git_root": ToolSpec("git_root", "Find Git repository root", Permission.GIT),
            "git_head": ToolSpec("git_head", "Read current Git commit", Permission.GIT),
        }

    def specs(self) -> tuple[ToolSpec, ...]:
        return tuple(self._specs.values())

    def get(self, name: str) -> ToolSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def resolve(self, name: str) -> Callable[..., object]:
        spec = self.get(name)
        self.permissions.require(spec.permission)
        handlers: dict[str, Callable[..., object]] = {
            "read_file": self.files.read,
            "write_file": self.files.write,
            "run_command": self.shell.run,
            "scan_workspace": self.scanner.scan,
            "git_status": self.git.status,
            "git_diff": self.git.diff,
            "git_root": self.git.root,
            "git_head": self.git.head,
        }
        return handlers[name]

    def describe(self) -> list[dict[str, str]]:
        return [{"name": spec.name, "description": spec.description, "permission": spec.permission.value} for spec in self.specs()]
