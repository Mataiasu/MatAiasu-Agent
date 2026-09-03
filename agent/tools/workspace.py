from pathlib import Path


IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea", ".vscode"}


class WorkspaceScanner:
    """Read-only project scanner used before any execution step."""

    def scan(self, root: Path, max_files: int = 500) -> dict[str, object]:
        root = root.expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Workspace does not exist: {root}")
        files: list[str] = []
        extensions: dict[str, int] = {}
        for path in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if not path.is_file():
                continue
            rel = str(path.relative_to(root))
            files.append(rel)
            suffix = path.suffix.lower() or "[none]"
            extensions[suffix] = extensions.get(suffix, 0) + 1
            if len(files) >= max_files:
                break
        return {
            "root": str(root),
            "file_count": len(files),
            "files": sorted(files),
            "extensions": dict(sorted(extensions.items())),
            "truncated": len(files) >= max_files,
        }
