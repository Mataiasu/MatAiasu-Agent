from pathlib import Path

from .permissions import Permission, PermissionManager
from .tools.files import FileTool
from .tools.shell import ShellTool


class AgentExecutor:
    """Executes only explicit tool operations approved by permissions."""

    def __init__(self, permissions: PermissionManager, files: FileTool | None = None, shell: ShellTool | None = None) -> None:
        self.permissions = permissions
        self.files = files or FileTool()
        self.shell = shell or ShellTool()

    def read_file(self, path: Path) -> str:
        self.permissions.require(Permission.READ_FILES)
        return self.files.read(path)

    def write_file(self, path: Path, content: str) -> None:
        self.permissions.require(Permission.WRITE_FILES)
        self.files.write(path, content)

    def run_command(self, command: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
        self.permissions.require(Permission.RUN_COMMANDS)
        return self.shell.run(command, cwd, timeout)
