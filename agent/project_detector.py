from __future__ import annotations

from pathlib import Path

MARKERS: dict[str, tuple[str, ...]] = {
    "python": ("pyproject.toml", "requirements.txt", "setup.py"),
    "godot": ("project.godot",),
    "node": ("package.json",),
    "rust": ("Cargo.toml",),
    "dotnet": ("*.csproj", "*.sln"),
    "java": ("pom.xml", "build.gradle", "build.gradle.kts"),
}


class ProjectDetector:
    """Detect likely project technologies from repository markers."""

    def detect(self, root: Path) -> dict[str, object]:
        root = root.expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Workspace does not exist: {root}")

        detected: list[str] = []
        marker_hits: dict[str, list[str]] = {}
        for kind, markers in MARKERS.items():
            hits: list[str] = []
            for marker in markers:
                hits.extend(str(p.relative_to(root)) for p in root.glob(marker) if p.is_file())
            if hits:
                detected.append(kind)
                marker_hits[kind] = sorted(set(hits))

        if not detected:
            detected.append("unknown")
        return {
            "root": str(root),
            "types": detected,
            "markers": marker_hits,
            "primary_type": detected[0],
        }
