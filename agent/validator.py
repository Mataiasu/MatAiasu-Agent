from dataclasses import dataclass
from pathlib import Path

from .tools.workspace import WorkspaceScanner


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    message: str


class Validator:
    def __init__(self, scanner: WorkspaceScanner | None = None) -> None:
        self.scanner = scanner or WorkspaceScanner()

    def workspace(self, root: Path) -> ValidationResult:
        try:
            result = self.scanner.scan(root)
        except (OSError, ValueError) as exc:
            return ValidationResult(False, str(exc))
        if result["file_count"] == 0:
            return ValidationResult(False, "Workspace contains no files")
        return ValidationResult(True, f"Workspace valid: {result['file_count']} files")

    def command(self, returncode: int, stdout: str, stderr: str) -> ValidationResult:
        if returncode == 0:
            return ValidationResult(True, stdout.strip() or "Command completed successfully")
        detail = stderr.strip() or stdout.strip() or f"Command exited with code {returncode}"
        return ValidationResult(False, detail)
