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
            "git_log": ToolSpec("git_log", "Inspect recent Git commits", Permission.GIT),
            "git_branches": ToolSpec("git_branches", "List local Git branches", Permission.GIT),
            "git_remote": ToolSpec("git_remote", "Inspect configured Git remotes", Permission.GIT),
            "git_add": ToolSpec("git_add", "Stage selected files in Git", Permission.GIT),
            "git_commit": ToolSpec("git_commit", "Create a Git commit", Permission.GIT),
            "git_fetch": ToolSpec("git_fetch", "Fetch Git remotes and prune stale refs", Permission.GIT),
            "git_pull": ToolSpec("git_pull", "Fast-forward Git working tree from its upstream", Permission.GIT),
            "git_push": ToolSpec("git_push", "Push the current Git branch to its upstream", Permission.GIT),
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
            "git_log": self.git.log,
            "git_branches": self.git.branches,
            "git_remote": self.git.remote,
            "git_add": self.git.add,
            "git_commit": self.git.commit,
            "git_fetch": self.git.fetch,
            "git_pull": self.git.pull,
            "git_push": self.git.push,
        }
        return handlers[name]

    def describe(self) -> list[dict[str, str]]:
        return [{"name": spec.name, "description": spec.description, "permission": spec.permission.value} for spec in self.specs()]
