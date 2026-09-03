from pathlib import Path

from .shell import ShellTool


class GitTool:
    """Read-only Git inspection helpers."""

    def __init__(self, shell: ShellTool | None = None) -> None:
        self.shell = shell or ShellTool()

    def status(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "status", "--short", "--branch"], cwd)

    def diff(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "diff", "--"], cwd)

    def root(self, cwd: Path) -> tuple[int, str, str]:
        return self.shell.run(["git", "rev-parse", "--show-toplevel"], cwd)
