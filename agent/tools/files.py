from __future__ import annotations

import os
import tempfile
from pathlib import Path


class FileTool:
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def write(self, path: Path, content: str) -> None:
        """Atomically replace a UTF-8 text file."""
        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise

    def list(self, root: Path) -> list[str]:
        return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
