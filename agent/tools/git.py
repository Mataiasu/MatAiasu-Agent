from __future__ import annotations

from pathlib import Path

from .shell import ShellTool


class GitTool:
    """Git operations executed through the controlled shell tool."""

    def __init__(self, shell: ShellTool | None = None) -> None:
        self.shell = shell or ShellTool()

    def status(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "status", "--short", "--branch"], cwd)

    def diff(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "diff", "--"], cwd)

    def root(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "rev-parse", "--show-toplevel"], cwd)

    def head(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "rev-parse", "HEAD"], cwd)

    def log(self, cwd: Path, limit: int = 10) -> tuple[int, str, str]:
        limit = max(1, min(int(limit), 100))
        return self.shell.run(["git", "log", f"-n{limit}", "--oneline", "--decorate"], cwd)

    def branches(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "branch", "--list"], cwd)

    def remote(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "remote", "-v"], cwd)

    def add(self, cwd: Path, paths: list[str]) -> tuple[int, str, str]:
        if not paths:
            raise ValueError("At least one path is required")
        return self.shell.run(["git", "add", "--", *paths], cwd)

    def commit(self, cwd: Path, message: str) -> tuple[int, str, str]:
        message = message.strip()
        if not message:
            raise ValueError("Commit message cannot be empty")
        return self.shell.run(["git", "commit", "-m", message], cwd)

    def fetch(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "fetch", "--all", "--prune"], cwd)

    def pull(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "pull", "--ff-only"], cwd)

    def push(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "push"], cwd)
