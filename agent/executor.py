from pathlib import Path

from .permissions import Permission, PermissionManager
from .tools.files import FileTool
from .tools.policy import WorkspacePolicy
from .tools.shell import ShellTool


class AgentExecutor:
    """Executes only explicit tool operations approved by permissions."""

    def __init__(self, permissions: PermissionManager, files: FileTool | None = None, shell: ShellTool | None = None) -> None:
        self.permissions = permissions
        self.files = files or FileTool()
        self.shell = shell or ShellTool()

    def read_file(self, path: Path, policy: WorkspacePolicy | None = None) -> str:
        self.permissions.require(Permission.READ_FILES)
        target = policy.resolve(path) if policy else path
        return self.files.read(target)

    def write_file(self, path: Path, content: str, policy: WorkspacePolicy | None = None) -> None:
        self.permissions.require(Permission.WRITE_FILES)
        target = policy.resolve(path) if policy else path
        self.files.write(target, content)

    def run_command(
        self,
        command: list[str],
        cwd: Path,
        timeout: int = 120,
        policy: WorkspacePolicy | None = None,
    ) -> tuple[int, str, str]:
        self.permissions.require(Permission.RUN_COMMANDS)
        working_dir = policy.cwd(cwd) if policy else cwd
        return self.shell.run(command, working_dir, timeout)
