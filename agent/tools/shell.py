import subprocess
from pathlib import Path


class ShellTool:
    """Controlled subprocess runner. Network/destructive policy belongs to permissions."""

    def run(self, command: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
