from pathlib import Path


class WorkspacePolicy:
    """Restrict file and process operations to an approved workspace."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        if not self.root.is_dir():
            raise FileNotFoundError(f"Workspace does not exist: {self.root}")

    def resolve(self, path: Path) -> Path:
        candidate = path.expanduser()
        if not candidate.is_absolute():
            candidate = self.root / candidate
        candidate = candidate.resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise PermissionError(f"Path outside workspace: {candidate}")
        return candidate

    def cwd(self, path: Path) -> Path:
        candidate = self.resolve(path)
        if not candidate.is_dir():
            raise NotADirectoryError(candidate)
        return candidate
